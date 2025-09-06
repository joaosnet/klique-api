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

        logger.info(f'Processando prompt: {prompt}')

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

        # Filtro 1: Ignora webhooks de confirmação
        #  (message.ack) silenciosamente
        if 'event' in data and data['event'] == 'message.ack':
            # Silencioso para acks de status,
            #  mas loga outros acks discretamente
            if data.get('payload', {}).get('chat_id') != 'status@broadcast':
                logger.debug('📨 Message ACK recebido')
            return {'status': 'ok'}

        # Filtro 2: Ignora eventos específicos silenciosamente
        event_type = data.get('event', '')
        ignored_events = [
            'message.revoke',
            'group.join',
            'group.leave',
            'user.status',
        ]
        if event_type in ignored_events:
            logger.debug(f'⚠️ Evento ignorado: {event_type}')
            return {'status': 'ok'}

        # Filtro 3: Ignora actions específicas (como message_edited)
        action = data.get('action', '')
        ignored_actions = [
            'message_edited',
            'message_deleted',
        ]
        if action in ignored_actions:
            logger.debug(f'✏️ Ação ignorada: {action}')
            return {'status': 'ok'}

        # Filtro 4: Verifica se tem conteúdo processável
        if 'message' not in data and 'image' not in data:
            logger.debug('📭 Webhook sem conteúdo processável')
            return {'status': 'ok'}

        # Verifica se a mensagem já foi processada (evita duplicatas)
        message_id = data.get('message', {}).get('id')
        if message_id and is_message_processed(message_id):
            logger.debug(f'🔄 Mensagem duplicata (ID: {message_id})')
            return {'status': 'ok'}

        # Extrai o prompt
        prompt = data.get('message', {}).get('text')
        if not prompt and 'image' in data:
            prompt = data.get('image', {}).get('caption')

        if not prompt:
            logger.debug('📝 Webhook sem prompt')
            return {'status': 'ok'}

        # Filtro 5: Ignora mensagens do próprio bot (evita loops)
        bot_prefixes = [
            'Sua imagem gerada a partir de:',
            'Gerado por Klique AI:',
        ]
        if any(prompt.startswith(prefix) for prefix in bot_prefixes):
            logger.debug('🤖 Mensagem do próprio bot ignorada')
            return {'status': 'ok'}

        # Valida remetente
        sender_phone = data.get('sender_id')
        if not sender_phone:
            logger.warning('❌ Remetente não identificado')
            return {'status': 'ok'}

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
