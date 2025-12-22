"""
Serviço de integração com Mercado Pago para pagamentos PIX.
"""

import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx

from ..config import CREDITS_PER_REAL, MP_ACCESS_TOKEN, MP_WEBHOOK_SECRET
from ..logger import logger

# URL base da API do Mercado Pago
MP_API_BASE = 'https://api.mercadopago.com'

# HTTP Status Codes
HTTP_OK = 200
HTTP_CREATED = 201


class MercadoPagoService:
    """Serviço para integração com a API do Mercado Pago."""

    def __init__(self):
        self.access_token = MP_ACCESS_TOKEN
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }

    async def create_pix_payment(
        self,
        amount: float,
        user_email: str,
        user_id: str,
        description: str = 'Créditos Klique Natal',
    ) -> dict:
        """
        Cria uma cobrança PIX no Mercado Pago.

        Args:
            amount: Valor em R$ (mínimo R$ 1,00)
            user_email: Email do usuário pagador
            user_id: ID do usuário no sistema
            description: Descrição do pagamento

        Returns:
            dict com dados do PIX (qr_code, copy_paste, etc)
        """
        if not self.access_token:
            logger.error('MP_ACCESS_TOKEN não configurado')
            return {'success': False, 'error': 'Mercado Pago não configurado'}

        # Calcular créditos baseado no valor
        credits_amount = int(amount * CREDITS_PER_REAL)

        # Data de expiração: 24 horas
        expiration = datetime.now(timezone.utc) + timedelta(hours=24)

        payload = {
            'transaction_amount': amount,
            'description': f'{description} ({credits_amount} créditos)',
            'payment_method_id': 'pix',
            'payer': {
                'email': user_email,
            },
            'date_of_expiration': expiration.isoformat(),
            # Para identificar o usuário no webhook
            'external_reference': user_id,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f'{MP_API_BASE}/v1/payments',
                    json=payload,
                    headers=self.headers,
                    timeout=30.0,
                )

                if response.status_code == HTTP_CREATED:
                    data = response.json()
                    pix_data = data.get('point_of_interaction', {}).get(
                        'transaction_data', {}
                    )

                    result = {
                        'success': True,
                        'payment_id': str(data.get('id')),
                        'status': data.get('status'),
                        'amount': amount,
                        'credits_amount': credits_amount,
                        'qr_code': pix_data.get('qr_code'),
                        'qr_code_base64': pix_data.get('qr_code_base64'),
                        'copy_paste': pix_data.get('qr_code'),
                        'expiration_date': expiration,
                    }

                    logger.info(
                        f'PIX criado: {result["payment_id"]} - '
                        f'R$ {amount} - {credits_amount} créditos'
                    )
                    return result

                else:
                    error_data = response.json()
                    logger.error(
                        f'Erro ao criar PIX: '
                        f'{response.status_code} - {error_data}'
                    )
                    return {
                        'success': False,
                        'error': error_data.get(
                            'message', 'Erro ao criar pagamento'
                        ),
                    }

        except Exception as e:
            logger.error(f'Exceção ao criar PIX: {e}', exc_info=True)
            return {'success': False, 'error': str(e)}

    async def get_payment_status(self, payment_id: str) -> dict:
        """
        Consulta o status de um pagamento.

        Args:
            payment_id: ID do pagamento no Mercado Pago

        Returns:
            dict com status e dados do pagamento
        """
        if not self.access_token:
            return {'success': False, 'error': 'Mercado Pago não configurado'}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f'{MP_API_BASE}/v1/payments/{payment_id}',
                    headers=self.headers,
                    timeout=30.0,
                )

                if response.status_code == HTTP_OK:
                    data = response.json()
                    return {
                        'success': True,
                        'payment_id': str(data.get('id')),
                        'status': data.get('status'),
                        'status_detail': data.get('status_detail'),
                        'amount': data.get('transaction_amount'),
                        'external_reference': data.get('external_reference'),
                        'date_approved': data.get('date_approved'),
                    }

                else:
                    error_data = response.json()
                    return {
                        'success': False,
                        'error': error_data.get(
                            'message', 'Erro ao consultar'
                        ),
                    }

        except Exception as e:
            logger.error(f'Exceção ao consultar pagamento: {e}', exc_info=True)
            return {'success': False, 'error': str(e)}

    @staticmethod
    def verify_webhook_signature(
        x_signature: Optional[str],
        x_request_id: Optional[str],
        data_id: str,
    ) -> bool:
        """
        Valida a assinatura do webhook do Mercado Pago.

        Args:
            x_signature: Header x-signature do request
            x_request_id: Header x-request-id do request
            data_id: ID do dado (payment_id)

        Returns:
            True se a assinatura for válida
        """
        if not MP_WEBHOOK_SECRET:
            logger.warning(
                'MP_WEBHOOK_SECRET não configurado - pulando validação'
            )
            return (
                True  # Sem secret, aceita tudo (não recomendado em produção)
            )

        if not x_signature:
            return False

        try:
            # Extrair ts e v1 da signature
            parts = dict(part.split('=') for part in x_signature.split(','))
            ts = parts.get('ts')
            v1 = parts.get('v1')

            if not ts or not v1:
                return False

            # Criar template da string a ser assinada
            template = f'id:{data_id};request-id:{x_request_id};ts:{ts};'

            # Calcular HMAC
            expected = hmac.new(
                MP_WEBHOOK_SECRET.encode(),
                template.encode(),
                hashlib.sha256,
            ).hexdigest()

            return hmac.compare_digest(expected, v1)

        except Exception as e:
            logger.error(f'Erro ao validar webhook: {e}')
            return False


# Instância singleton do serviço
mercadopago_service = MercadoPagoService()
