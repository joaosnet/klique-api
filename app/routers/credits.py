"""
Router para gerenciamento de créditos do usuário.
Permite consultar saldo, usar créditos e ver histórico.
"""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from ..config import FREE_CREDITS_PER_USER
from ..database import (
    get_payment_transactions_collection,
    get_user_credits_collection,
)
from ..dependencies import get_current_active_user
from ..logger import logger
from .schemas import (
    CreditHistoryItem,
    CreditHistoryResponse,
    UseCreditsResponse,
    User,
    UserCreditsBalance,
)

router = APIRouter(prefix='/api/credits', tags=['credits'])


async def get_or_create_user_credits(user_id: str, db_credits=None):
    """
    Obtém ou cria o registro de créditos do usuário.

    Se o usuário não tiver registro, cria um com os créditos grátis.
    """
    if db_credits is None:
        db_credits = get_user_credits_collection()

    credits = await db_credits.find_one({'user_id': user_id})

    if not credits:
        # Criar registro inicial com créditos grátis
        now = datetime.now(timezone.utc)
        credits = {
            'user_id': user_id,
            'free_credits': FREE_CREDITS_PER_USER,
            'paid_credits': 0,
            'total_generated': 0,
            'created_at': now,
            'updated_at': now,
        }
        await db_credits.insert_one(credits)
        logger.info(f'Créditos iniciais criados para usuário {user_id}')

    return credits


async def check_user_has_credits(user_id: str) -> dict:
    """
    Verifica se o usuário tem créditos disponíveis.

    Returns:
        dict com 'has_credits', 'total', 'free', 'paid'
    """
    credits = await get_or_create_user_credits(user_id)
    total = credits.get('free_credits', 0) + credits.get('paid_credits', 0)

    return {
        'has_credits': total > 0,
        'total': total,
        'free': credits.get('free_credits', 0),
        'paid': credits.get('paid_credits', 0),
    }


async def use_one_credit(user_id: str) -> dict:
    """
    Consome 1 crédito do usuário.

    Prioridade: primeiro usa créditos grátis, depois pagos.

    Returns:
        dict com 'success', 'message', 'remaining', 'credit_type'
    """
    db_credits = get_user_credits_collection()
    credits = await get_or_create_user_credits(user_id, db_credits)

    free = credits.get('free_credits', 0)
    paid = credits.get('paid_credits', 0)

    if free <= 0 and paid <= 0:
        return {
            'success': False,
            'message': 'Sem créditos disponíveis',
            'remaining': 0,
            'credit_type': None,
        }

    # Usar crédito grátis primeiro
    if free > 0:
        update_field = 'free_credits'
        credit_type = 'free'
    else:
        update_field = 'paid_credits'
        credit_type = 'paid'

    await db_credits.update_one(
        {'user_id': user_id},
        {
            '$inc': {update_field: -1, 'total_generated': 1},
            '$set': {'updated_at': datetime.now(timezone.utc)},
        },
    )

    remaining = (free + paid) - 1
    logger.info(
        f'Crédito ({credit_type}) usado pelo usuário {user_id}. Restantes: {remaining}'  # noqa: E501
    )

    return {
        'success': True,
        'message': 'Crédito utilizado com sucesso',
        'remaining': remaining,
        'credit_type': credit_type,
    }


async def add_paid_credits(user_id: str, amount: int) -> dict:
    """
    Adiciona créditos pagos ao usuário.

    Args:
        user_id: ID do usuário
        amount: Quantidade de créditos a adicionar

    Returns:
        dict com 'success', 'new_balance'
    """
    db_credits = get_user_credits_collection()
    await get_or_create_user_credits(user_id, db_credits)

    result = await db_credits.update_one(
        {'user_id': user_id},
        {
            '$inc': {'paid_credits': amount},
            '$set': {'updated_at': datetime.now(timezone.utc)},
        },
    )

    if result.modified_count > 0:
        credits = await db_credits.find_one({'user_id': user_id})
        new_balance = credits.get('free_credits', 0) + credits.get(
            'paid_credits', 0
        )
        logger.info(
            f'{amount} créditos adicionados ao usuário {user_id}. '
            f'Novo saldo: {new_balance}'
        )
        return {'success': True, 'new_balance': new_balance}

    return {'success': False, 'new_balance': 0}


# ========================================
# API Endpoints
# ========================================


@router.get('/balance', response_model=UserCreditsBalance)
async def get_credits_balance(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Retorna o saldo de créditos do usuário logado."""
    try:
        user_id = str(current_user.get('_id'))
        credits = await get_or_create_user_credits(user_id)

        free = credits.get('free_credits', 0)
        paid = credits.get('paid_credits', 0)

        return UserCreditsBalance(
            free_credits=free,
            paid_credits=paid,
            total_credits=free + paid,
            total_generated=credits.get('total_generated', 0),
        )

    except Exception as e:
        logger.error(f'Erro ao consultar créditos: {e}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Erro ao consultar saldo de créditos',
        )


@router.post('/use', response_model=UseCreditsResponse)
async def use_credit(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Consome 1 crédito do usuário.

    Este endpoint é chamado internamente pelo processamento de imagens.
    """
    try:
        user_id = str(current_user.get('_id'))
        result = await use_one_credit(user_id)

        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=result['message'],
            )

        return UseCreditsResponse(
            success=True,
            message=result['message'],
            remaining_credits=result['remaining'],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Erro ao usar crédito: {e}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Erro ao usar crédito',
        )


@router.get('/history', response_model=CreditHistoryResponse)
async def get_credits_history(
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: int = 50,
):
    """Retorna o histórico de uso e compras de créditos."""
    try:
        user_id = str(current_user.get('_id'))
        db_transactions = get_payment_transactions_collection()

        # Buscar transações de pagamento
        transactions = (
            await db_transactions
            .find({'user_id': user_id})
            .sort('created_at', -1)
            .limit(limit)
            .to_list(length=limit)
        )

        items = []
        for tx in transactions:
            item_type = (
                'purchase' if tx.get('status') == 'approved' else 'pending'
            )
            items.append(
                CreditHistoryItem(
                    type=item_type,
                    amount=tx.get('credits_amount', 0),
                    description=(
                        f'Compra de {tx.get("credits_amount", 0)} créditos - '
                        f'R$ {tx.get("amount", 0):.2f}'
                    ),
                    created_at=tx.get(
                        'created_at', datetime.now(timezone.utc)
                    ),
                )
            )

        return CreditHistoryResponse(
            items=items,
            total_items=len(items),
        )

    except Exception as e:
        logger.error(f'Erro ao consultar histórico: {e}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Erro ao consultar histórico de créditos',
        )
