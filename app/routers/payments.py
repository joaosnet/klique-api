"""
Router para pagamentos PIX via Mercado Pago.
"""

from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status

from ..config import (
    MIN_CREDITS_QUANTITY,
    MIN_PAYMENT_AMOUNT,
    MIN_PRICE_PER_CREDIT,
)
from ..database import get_payment_transactions_collection
from ..dependencies import get_current_active_user
from ..logger import logger
from ..services.mercadopago import mercadopago_service
from .credits import add_paid_credits
from .schemas import (
    CreatePixPaymentRequest,
    CreatePixPaymentResponse,
    PaymentConfigResponse,
    PaymentStatusResponse,
    User,
)

router = APIRouter(prefix='/api/payments', tags=['payments'])


@router.get('/config', response_model=PaymentConfigResponse)
async def get_payment_config():
    """Retorna as configurações e limites de pagamento."""
    return PaymentConfigResponse(
        min_payment_amount=MIN_PAYMENT_AMOUNT,
        min_price_per_credit=MIN_PRICE_PER_CREDIT,
        min_quantity=MIN_CREDITS_QUANTITY,
    )


@router.post('/pix/create', response_model=CreatePixPaymentResponse)
async def create_pix_payment(
    request: CreatePixPaymentRequest,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Cria uma cobrança PIX para compra de créditos.

    O valor mínimo é R$ 1,00 e cada R$ 1,00 equivale a 1 crédito.
    """
    try:
        # Validar valor mínimo
        if request.amount < MIN_PAYMENT_AMOUNT:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Valor mínimo é R$ {MIN_PAYMENT_AMOUNT:.2f}',
            )

        user_id = str(current_user.get('_id'))
        user_email = current_user.get('email')

        # Criar pagamento no Mercado Pago
        result = await mercadopago_service.create_pix_payment(
            amount=request.amount,
            user_email=user_email,
            user_id=user_id,
            credits_count=request.credits_count,
        )

        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=result.get('error', 'Erro ao criar pagamento'),
            )

        # Salvar transação no banco
        db_transactions = get_payment_transactions_collection()
        transaction = {
            'user_id': user_id,
            'mp_payment_id': result['payment_id'],
            'amount': request.amount,
            'credits_amount': result['credits_amount'],
            'status': 'pending',
            'pix_qr_code': result.get('qr_code'),
            'pix_qr_code_base64': result.get('qr_code_base64'),
            'pix_copy_paste': result.get('copy_paste'),
            'expiration_date': result.get('expiration_date'),
            'created_at': datetime.now(timezone.utc),
            'paid_at': None,
        }
        await db_transactions.insert_one(transaction)

        return CreatePixPaymentResponse(
            success=True,
            payment_id=result['payment_id'],
            amount=request.amount,
            credits_amount=result['credits_amount'],
            qr_code=result.get('qr_code', ''),
            qr_code_base64=result.get('qr_code_base64', ''),
            copy_paste=result.get('copy_paste', ''),
            expiration_date=result['expiration_date'],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Erro ao criar PIX: {e}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Erro ao criar pagamento',
        )


@router.get('/status/{payment_id}', response_model=PaymentStatusResponse)
async def get_payment_status(
    payment_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Consulta o status de um pagamento."""
    try:
        user_id = str(current_user.get('_id'))
        db_transactions = get_payment_transactions_collection()

        # Buscar transação local
        transaction = await db_transactions.find_one({
            'mp_payment_id': payment_id,
            'user_id': user_id,
        })

        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Pagamento não encontrado',
            )

        # Se ainda pendente, consultar Mercado Pago
        if transaction.get('status') == 'pending':
            mp_status = await mercadopago_service.get_payment_status(
                payment_id
            )

            if (
                mp_status.get('success')
                and mp_status.get('status') == 'approved'
            ):
                # Atualizar transação e liberar créditos
                await _process_approved_payment(
                    transaction, mp_status.get('date_approved')
                )
                transaction['status'] = 'approved'
                transaction['paid_at'] = mp_status.get('date_approved')

        return PaymentStatusResponse(
            payment_id=payment_id,
            status=transaction.get('status', 'pending'),
            amount=transaction.get('amount', 0),
            credits_amount=transaction.get('credits_amount', 0),
            paid_at=transaction.get('paid_at'),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Erro ao consultar pagamento: {e}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Erro ao consultar pagamento',
        )


@router.post('/webhook')
async def mercadopago_webhook(
    request: Request,
    x_signature: Optional[str] = Header(None),
    x_request_id: Optional[str] = Header(None),
):
    """
    Webhook para receber notificações do Mercado Pago.

    O Mercado Pago envia notificações quando o status do pagamento muda.
    """
    try:
        body = await request.json()
        logger.info(f'Webhook recebido: {body}')

        # Verificar tipo de notificação
        action = body.get('action')
        data = body.get('data', {})
        payment_id = str(data.get('id', ''))

        if not payment_id:
            return {'status': 'ignored', 'reason': 'no payment id'}

        # Validar assinatura (opcional mas recomendado)
        if not mercadopago_service.verify_webhook_signature(
            x_signature, x_request_id, payment_id
        ):
            logger.warning(f'Assinatura inválida para webhook: {payment_id}')
            # Não rejeitar, apenas logar (pode ser teste)

        # Processar apenas pagamentos aprovados
        if action == 'payment.updated':
            # Consultar status atual no Mercado Pago
            mp_status = await mercadopago_service.get_payment_status(
                payment_id
            )

            if (
                mp_status.get('success')
                and mp_status.get('status') == 'approved'
            ):
                db_transactions = get_payment_transactions_collection()
                transaction = await db_transactions.find_one({
                    'mp_payment_id': payment_id
                })

                if transaction and transaction.get('status') != 'approved':
                    await _process_approved_payment(
                        transaction, mp_status.get('date_approved')
                    )
                    logger.info(f'Pagamento {payment_id} aprovado via webhook')

        return {'status': 'ok'}

    except Exception as e:
        logger.error(f'Erro no webhook: {e}', exc_info=True)
        # Retornar 200 para não reprocessar
        return {'status': 'error', 'message': str(e)}


async def _process_approved_payment(transaction: dict, paid_at=None):
    """
    Processa um pagamento aprovado: atualiza status e libera créditos.
    """
    db_transactions = get_payment_transactions_collection()
    user_id = transaction.get('user_id')
    credits_amount = transaction.get('credits_amount', 0)
    mp_payment_id = transaction.get('mp_payment_id')

    # Atualizar transação
    await db_transactions.update_one(
        {'mp_payment_id': mp_payment_id},
        {
            '$set': {
                'status': 'approved',
                'paid_at': paid_at or datetime.now(timezone.utc),
            }
        },
    )

    # Adicionar créditos ao usuário
    result = await add_paid_credits(user_id, credits_amount)

    if result.get('success'):
        logger.info(
            f'Créditos liberados: {credits_amount} para usuário {user_id}'
        )
    else:
        logger.error(f'Falha ao liberar créditos para {user_id}')
