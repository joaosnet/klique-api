import time
from collections import defaultdict

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from loguru import logger

from ..services.gemini import GeminiService, get_gemini_service
from ..services.whatsapp import WhatsAppService

router = APIRouter(
    prefix='/webhooks',
    tags=['webhooks'],
)

# Cache para evitar processamento duplicado de mensagens
message_cache = defaultdict(float)
CACHE_EXPIRY_SECONDS = 300  # 5 minutos


def cleanup_cache():
    """Remove entradas antigas do cache para evitar crescimento infinito"""
    current_time = time.time()
    expired_keys = [
        key
        for key, timestamp in message_cache.items()
        if current_time - timestamp > CACHE_EXPIRY_SECONDS
    ]
    for key in expired_keys:
        del message_cache[key]


def is_message_processed(message_id: str) -> bool:
    """Verifica se a mensagem já foi processada"""
    cleanup_cache()
    current_time = time.time()

    if message_id in message_cache:
        return True

    # Marca a mensagem como processada
    message_cache[message_id] = current_time
    return False


async def process_image_generation(
    data: dict, gemini_service: GeminiService
) -> None:
    """Processa a geração de imagem em background"""
    whatsapp_service = None
    try:
        # Extrai dados necessários
        prompt = data.get('message', {}).get('text')
        if not prompt and 'image' in data:
            prompt = data.get('image', {}).get('caption')

        sender_phone = data.get('sender_id')
        media_path = data.get('image', {}).get('media_path')

        whatsapp_service = WhatsAppService()
        image_bytes = None
        if media_path:
            image_bytes = await whatsapp_service.download_media(media_path)

        generated_bytes = await gemini_service.generate_image_from_prompt(
            prompt, image_bytes
        )

        if not generated_bytes:
            logger.warning(
                '⚠️ Gemini não conseguiu gerar imagem para este prompt'
            )

            # Envia mensagem explicativa para o usuário
            error_message = (
                'Desculpe, não consegui gerar uma '
                f"imagem para o prompt: '{prompt}'. "
                'Tente um prompt mais específico para geração'
                ' de imagem, como:\n'
                "• 'Crie uma imagem de um gato'\n"
                "• 'Desenhe uma paisagem de montanha'\n"
                "• 'Gere uma ilustração de um robô'"
            )

            await whatsapp_service.send_text_message(
                phone_number=sender_phone, message=error_message
            )
            return

        logger.success('✅ Imagem gerada! Enviando para o chat...')

        send_result = await whatsapp_service.send_image_message(
            phone_number=sender_phone,
            image_bytes=generated_bytes,
            caption=f"Sua imagem gerada a partir de: '{prompt}'",
        )

        if not send_result:
            logger.error('❌ Falha ao enviar a imagem')
            return

        logger.info('📤 Postando no status do WhatsApp...')
        # Posta a imagem no status usando status@broadcast
        await whatsapp_service.post_status_update(
            image_bytes=generated_bytes,
            caption=f"Gerado por Klique AI: '{prompt}'",
        )

        # Envia mensagem de sucesso ao usuário
        await whatsapp_service.send_text_message(
            phone_number=sender_phone,
            message='Sua imagem foi gerada com sucesso!',
        )

        logger.success('🎉 Processamento concluído com sucesso!')

    except Exception as e:
        logger.error(
            '❌ Erro no processamento em background:'
            f' {type(e).__name__}: {str(e)}'
        )
        logger.exception('Detalhes do erro:')
    finally:
        if whatsapp_service:
            await whatsapp_service.close()
            logger.debug('🔌 Conexão WhatsApp fechada')


def should_ignore_webhook(data: dict) -> tuple[bool, str]:
    """Verifica se o webhook deve ser ignorado e retorna (ignorar, motivo)"""
    # Lista de verificações de filtro
    filters = [
        # Filtro 1: message.ack
        (
            lambda d: 'event' in d and d['event'] == 'message.ack',
            lambda d: (
                logger.debug('📨 Message ACK recebido')
                if d.get('payload', {}).get('chat_id') != 'status@broadcast'
                else None,
                'message.ack',
            ),
        ),
        # Filtro 2: eventos ignorados
        (
            lambda d: d.get('event', '')
            in {'message.revoke', 'group.join', 'group.leave', 'user.status'},
            lambda d: (
                logger.debug(f'⚠️ Evento ignorado: {d.get("event", "")}'),
                d.get('event', ''),
            ),
        ),
        # Filtro 3: actions ignoradas
        (
            lambda d: d.get('action', '')
            in {'message_edited', 'message_deleted'},
            lambda d: (
                logger.debug(f'✏️ Ação ignorada: {d.get("action", "")}'),
                d.get('action', ''),
            ),
        ),
        # Filtro 4: sem conteúdo
        (
            lambda d: 'message' not in d and 'image' not in d,
            lambda d: (
                logger.debug('📭 Webhook sem conteúdo processável'),
                'no_content',
            ),
        ),
        # Filtro 5: duplicata
        (
            lambda d: (mid := d.get('message', {}).get('id'))
            and is_message_processed(mid),
            lambda d: (
                logger.debug(
                    '🔄 Mensagem duplicata (ID: '
                    f'{d.get("message", {}).get("id")})'
                ),
                'duplicate',
            ),
        ),
        # Filtro 6: sem prompt
        (
            lambda d: not (
                d.get('message', {}).get('text')
                or (
                    d.get('image', {}).get('caption') if 'image' in d else None
                )
            ),
            lambda d: (logger.debug('📝 Webhook sem prompt'), 'no_prompt'),
        ),
        # Filtro 7: mensagem do bot
        (
            lambda d: any(
                (
                    d.get('message', {}).get('text')
                    or d.get('image', {}).get('caption', '')
                ).startswith(prefix)
                for prefix in [
                    'Sua imagem gerada a partir de:',
                    'Gerado por Klique AI:',
                ]
            ),
            lambda d: (
                logger.debug('🤖 Mensagem do próprio bot ignorada'),
                'bot_message',
            ),
        ),
        # Filtro 8: sem remetente
        (
            lambda d: not d.get('sender_id'),
            lambda d: (
                logger.warning('❌ Remetente não identificado'),
                'no_sender',
            ),
        ),
    ]

    for condition, action in filters:
        if condition(data):
            _, reason = action(data)
            return True, reason

    return False, ''


@router.post('/whatsapp')
async def receive_whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    gemini_service: GeminiService = Depends(get_gemini_service),
):
    """
    Recebe webhooks do go-whatsapp e responde rapidamente.
    Processamento pesado é feito em background.
    """
    try:
        data = await request.json()
        logger.bind(payload=data).info('📄 Novo webhook recebido')

        ignore, reason = should_ignore_webhook(data)
        if ignore:
            return {'status': 'ok'}

        # Extrai o sender e envia mensagem de processamento
        sender = data.get('sender_id')
        if sender:
            whatsapp_service = WhatsAppService()
            await whatsapp_service.send_text_message(
                phone_number=sender, message='Processando sua imagem...'
            )
            await whatsapp_service.close()

        # Log mínimo para webhooks válidos
        logger.info('📱 Webhook processável recebido')

        # Agenda processamento em background e retorna 200 imediatamente
        background_tasks.add_task(
            process_image_generation, data, gemini_service
        )

        return {
            'status': 'accepted',
            'detail': 'Webhook agendado para processamento',
        }

    except Exception as e:
        logger.error(f'❌ Erro no webhook: {str(e)}')
        logger.exception('Detalhes do erro no webhook:')
        # Sempre retorna 200 para evitar reenvios do GOWA
        return {'status': 'error', 'detail': str(e)}
