from datetime import datetime  # noqa: I001

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from loguru import logger

from ..cache import (
    MessageCache,
    StatusImageCache,
)
from ..database import get_status_views_collection
from ..routers import schemas
from ..services.gemini import GeminiService
from ..services.whatsapp import WhatsAppService
from ..utils import extract_user_number, extract_primary_user_number
from ..webhook_dependencies import (
    WebhookDependencies,
    get_webhook_dependencies,
)

router = APIRouter(
    prefix='/webhooks',
    tags=['webhooks'],
)


def extract_prompt(data: dict) -> tuple[str | None, str]:
    """Extrai prompt de texto ou caption de imagem e o nome do remetente."""
    msg = data.get('message', {})
    sender_name = data.get('sender_name', 'Alguém')

    if text := msg.get('text'):
        return text, sender_name

    caption = data.get('image', {}).get('caption')
    return caption, sender_name


async def send_or_edit_failure(
    whatsapp_service: WhatsAppService,
    phone: str | None,
    processing_message_id: str | None,
) -> None:
    """Centraliza envio/edição de mensagem de falha."""
    if not phone:
        return
    failure_message = whatsapp_service.get_random_failure_message()
    if processing_message_id:
        edited = await whatsapp_service.edit_message(
            processing_message_id, failure_message
        )
        if not edited:
            await whatsapp_service.send_message(
                phone_number=phone, message=failure_message
            )
    else:
        await whatsapp_service.send_message(
            phone_number=phone, message=failure_message
        )


async def process_image_generation(
    data: dict,
    gemini_service: GeminiService,
    whatsapp_service: WhatsAppService,
    status_image_cache: StatusImageCache,
) -> None:
    """Processa a geração de imagem em background"""
    sender_phone = data.get('sender_id')  # Para enviar a resposta
    processing_message_id = data.get('processing_message_id')

    try:
        # Extrai dados necessários
        prompt, sender_name = extract_prompt(data)
        user_number = extract_primary_user_number(data)

        contact_name = sender_name
        if contact_name == 'Alguém' and user_number:
            contact_info = await whatsapp_service.get_contact_info(user_number)
            if contact_info and contact_info.get('name'):
                contact_name = contact_info.get('name')

        # Atualiza mensagem de processamento se possível
        if processing_message_id:
            await whatsapp_service.edit_message(
                processing_message_id,
                '🎨 Gerando sua imagem... Por favor, aguarde!',
            )

        media_path = data.get('image', {}).get('media_path')

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
            await send_or_edit_failure(
                whatsapp_service,
                sender_phone,
                processing_message_id,
            )
            return

        logger.success('✅ Imagem gerada! Enviando para o chat...')

        # Atualiza mensagem de processamento
        if processing_message_id:
            await whatsapp_service.edit_message(
                processing_message_id,
                '✅ Imagem gerada! Enviando para você...',
            )

        send_result = await whatsapp_service.send_image_message(
            phone_number=sender_phone,
            image_bytes=generated_bytes,
            caption=f'Imagem gerada para {contact_name}: {prompt}',
        )

        if not send_result:
            logger.error('❌ Falha ao enviar a imagem')
            return

        logger.info('📤 Postando no status do WhatsApp...')

        # Posta a imagem no status usando status@broadcast
        status_id = await whatsapp_service.post_status_update(
            image_bytes=generated_bytes,
            caption=f"Editado por: {sender_name} | Prompt: '{prompt}'",
        )

        # Salva a imagem e o ID do status no cache do MongoDB
        if status_id:
            await status_image_cache.save_status_image(generated_bytes)
            await status_image_cache.save_last_status_id(status_id)

        # Atualiza mensagem final
        if processing_message_id:
            await whatsapp_service.edit_message(
                processing_message_id,
                f'🎉 Processo concluído! Imagem enviada e publicada '
                f"no status para: '{prompt}'",
            )

        logger.success('🎉 Processamento concluído com sucesso!')

    except Exception as e:
        logger.error(
            '❌ Erro no processamento em background:'
            f' {type(e).__name__}: {str(e)}'
        )
        logger.exception('Detalhes do erro:')
        await send_or_edit_failure(
            whatsapp_service,
            sender_phone,
            processing_message_id,
        )


async def process_status_viewed_for_image_generation(
    data: dict,
    gemini_service: GeminiService,
    whatsapp_service: WhatsAppService,
    status_image_cache: StatusImageCache,
) -> None:
    """Gera uma nova imagem baseada na imagem anterior em cache
    quando alguém visualiza."""
    try:
        payload = data.get('payload', {})
        sender_id = payload.get('sender_id')

        if not sender_id:
            logger.warning(
                '❌ Sender ID não encontrado na visualização de status'
            )
            return

        user_number = extract_user_number(sender_id)

        viewer_name = None
        try:
            contact_info = await whatsapp_service.get_contact_info(user_number)
            viewer_name = contact_info.get('name') if contact_info else None
        except Exception as e:
            logger.debug(f'Erro ao buscar nome do contato {user_number}: {e}')

        if not viewer_name:
            viewer_name = f'*{user_number[-4:]}'

        logger.info(f'👁️ Status visualizado por {viewer_name} ({user_number})')

        cached_image_bytes = await status_image_cache.get_last_status_image()

        if cached_image_bytes:
            prompt = (
                f"Edite esta imagem adicionando o texto '{viewer_name}' "
                f'de forma criativa e elegante. Mantenha o estilo '
                f'original da imagem.'
            )
            logger.info(
                f'🎨 Editando imagem anterior em cache para {viewer_name}...'
            )

            new_image_bytes = await gemini_service.generate_image_from_prompt(
                prompt, cached_image_bytes
            )
        else:
            prompt = (
                f'Crie uma imagem criativa e elegante com o texto '
                f"'{viewer_name}' em destaque. Use cores vibrantes "
                f'e um design moderno.'
            )
            logger.info(
                f'🎨 Criando nova imagem para {viewer_name} '
                f'(sem cache disponível)...'
            )
            new_image_bytes = await gemini_service.generate_image_from_prompt(
                prompt, None
            )

        if not new_image_bytes:
            logger.warning('⚠️ Gemini não conseguiu gerar nova imagem')
            return

        logger.success('✅ Nova imagem gerada! Postando no status...')

        # Deleta o status antigo, se existir
        last_status_id = await status_image_cache.get_last_status_id()
        if last_status_id:
            logger.info(f'🗑️ Deletando status antigo: {last_status_id}')
            await whatsapp_service.delete_status(last_status_id)

        # Posta a nova imagem como status
        await whatsapp_service.post_status_update(
            image_bytes=new_image_bytes,
            caption=f'Visualizado por: {viewer_name} 👁️',
        )

        logger.success(
            f'🎉 Novo status gerado para visualização de {viewer_name}!'
        )

    except Exception as e:
        logger.error(f'❌ Erro ao processar visualização de status: {e}')
        logger.exception('Detalhes do erro:')


async def process_status_view(data: dict) -> None:
    """Processa e salva a visualização de status no banco de dados."""
    try:
        sender_id = data.get('sender_id')
        timestamp_str = data.get('timestamp')

        if not sender_id or not timestamp_str:
            payload = data.get('payload', {})
            sender_id = sender_id or payload.get('sender_id')
            timestamp_str = timestamp_str or payload.get('timestamp')

        logger.debug(
            f'🔍 Processando status view - sender_id: {sender_id}, '
            f'timestamp: {timestamp_str}'
        )

        if not sender_id or not timestamp_str:
            logger.warning(
                f'❌ Dados de visualização de status incompletos - '
                f'sender_id: {sender_id}, timestamp: {timestamp_str}'
            )
            logger.debug(f'📋 Dados completos: {data}')
            return

        user_number = extract_user_number(sender_id)

        viewed_at = datetime.fromisoformat(
            timestamp_str.replace('Z', '+00:00')
        )

        status_view = schemas.StatusView(
            user_number=user_number,
            viewed_at=viewed_at,
        )

        try:
            status_views_collection = get_status_views_collection()
            await status_views_collection.insert_one(status_view.model_dump())
            logger.info(f'👁️ Status visualizado por {user_number} salvo no DB.')
        except Exception as db_e:
            logger.warning(f'⚠️ Não foi possível salvar no banco: {db_e}')
            logger.info(
                f'👁️ Status visualizado por {user_number} (não salvo no DB).'
            )

    except Exception as e:
        logger.error(f'❌ Erro ao processar visualização de status: {e}')
        logger.exception('Detalhes do erro:')


async def should_ignore_webhook(
    data: dict, message_cache: MessageCache
) -> tuple[bool, str]:
    """Verifica se o webhook deve ser ignorado e retorna (ignorar, motivo)"""

    if (
        data.get('event') == 'message.ack'
        and data.get('payload', {}).get('chat_id') == 'status@broadcast'
        and data.get('payload', {}).get('receipt_type') != 'read'
    ):
        logger.debug('📨 ACK de entrega de status (não read) - ignorando')
        return True, 'status_delivery_ack'

    prompt_cached, _ = extract_prompt(data)

    # Verifica se a mensagem já foi processada (usando cache MongoDB)
    message_id = data.get('message', {}).get('id')
    if message_id and await message_cache.is_message_processed(message_id):
        logger.debug(f'🔄 Mensagem duplicata (ID: {message_id})')
        return True, 'duplicate'

    filters = [
        (
            lambda d: d.get('event') == 'message.ack',
            lambda d: (
                logger.debug('📨 Message ACK (não status) recebido'),
                'message.ack',
            ),
        ),
        (
            lambda d: d.get('event', '')
            in {'message.revoke', 'group.join', 'group.leave', 'user.status'},
            lambda d: (
                logger.debug(f'⚠️ Evento ignorado: {d.get("event", "")}'),
                d.get('event', ''),
            ),
        ),
        (
            lambda d: d.get('action', '')
            in {'message_edited', 'message_deleted'},
            lambda d: (
                logger.debug(f'✏️ Ação ignorada: {d.get("action", "")}'),
                d.get('action', ''),
            ),
        ),
        (
            lambda d: 'message' not in d and 'image' not in d,
            lambda d: (
                logger.debug('📭 Webhook sem conteúdo processável'),
                'no_content',
            ),
        ),
        (
            lambda d: not prompt_cached,
            lambda d: (logger.debug('📝 Webhook sem prompt'), 'no_prompt'),
        ),
        (
            lambda d: prompt_cached
            and any(
                prompt_cached.startswith(prefix)
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
    deps: WebhookDependencies = Depends(get_webhook_dependencies),
):
    """
    Recebe webhooks do go-whatsapp e responde rapidamente.
    Processamento pesado é feito em background.
    """
    try:
        data = await request.json()
        user_number = extract_primary_user_number(data)
        contact_info = await WhatsAppService().get_contact_info(
            phone_number=user_number
        )

        logger.bind(payload=data).info(
            f'Contato: {contact_info} recebeu sua mensagem'
        )

        if (
            data.get('event') == 'message.ack'
            and data.get('payload', {}).get('chat_id') == 'status@broadcast'
            and data.get('payload', {}).get('receipt_type') == 'read'
        ):
            logger.info('👁️ Visualização de status detectada!')
            background_tasks.add_task(process_status_view, data)
            background_tasks.add_task(
                process_status_viewed_for_image_generation,
                data,
                deps.gemini_service,
                deps.whatsapp_service,
                deps.status_image_cache,
            )
            return {'status': 'accepted', 'detail': 'Status view processed'}

        if data.get('event') == 'status.viewed':
            logger.info('👁️ Webhook de visualização de status recebido.')
            background_tasks.add_task(process_status_view, data)
            background_tasks.add_task(
                process_status_viewed_for_image_generation,
                data,
                deps.gemini_service,
                deps.whatsapp_service,
                deps.status_image_cache,
            )
            return {'status': 'accepted', 'detail': 'Status view processed'}

        ignore, reason = await should_ignore_webhook(data, deps.message_cache)
        if ignore:
            return {'status': 'ok', 'reason': reason}

        sender = data.get('sender_id')
        processing_message_id = None

        if sender:
            processing_message = (
                deps.whatsapp_service.get_random_processing_message()
            )
            processing_message_id = await deps.whatsapp_service.send_message(
                phone_number=sender, message=processing_message
            )

        logger.info('📱 Webhook processável recebido, agendando task...')

        task_data = {
            **data,
            'processing_message_id': processing_message_id,
        }
        background_tasks.add_task(
            process_image_generation,
            task_data,
            deps.gemini_service,
            deps.whatsapp_service,
            deps.status_image_cache,
        )

        return {
            'status': 'accepted',
            'detail': 'Webhook agendado para processamento',
        }

    except Exception as e:
        logger.error(f'❌ Erro no webhook: {str(e)}')
        logger.exception('Detalhes do erro no webhook:')
        return {'status': 'error', 'detail': str(e)}
    finally:
        logger.debug('🔌 Webhook principal finalizado')
