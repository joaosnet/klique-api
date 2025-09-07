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
from ..command import (
    parse_command,
    CommandOperation,
    HELP_MESSAGE,
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
    """Centraliza envio/edição de mensagem de falha com sugestão de ajuda."""
    if not phone:
        return
    base_message = whatsapp_service.get_random_failure_message()
    failure_message = f"{base_message} Envie 'ajuda' para instruções."
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


async def _save_session_data(
    user_session_cache,
    user_number: str,
    session_data: dict,
) -> None:
    """Salva dados da sessão de forma consistente."""
    try:
        if user_number:
            prompt = session_data.get('prompt')
            generated_bytes = session_data.get('generated_bytes')
            image_bytes = session_data.get('image_bytes')
            status_id = session_data.get('status_id')

            if prompt:
                await user_session_cache.save_prompt(user_number, prompt)
            if generated_bytes:
                await user_session_cache.save_generated_image(
                    user_number, generated_bytes
                )
            # Se havia imagem base usada para edição (image_bytes), armazenar
            if image_bytes:
                await user_session_cache.save_base_image(
                    user_number, image_bytes
                )
            if status_id:
                await user_session_cache.save_status_id(user_number, status_id)
    except Exception as sess_e:  # noqa: BLE001
        logger.warning(f'⚠️ Falha ao atualizar sessão do usuário: {sess_e}')


async def process_image_generation(
    data: dict,
    gemini_service: GeminiService,
    whatsapp_service: WhatsAppService,
    user_session_cache,
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

        # Salva a imagem e o ID do status no cache global
        if status_id:
            await status_image_cache.save_status_image(generated_bytes)
            await status_image_cache.save_last_status_id(status_id)

        # Atualiza sessão por usuário (unifica comandos)
        session_data = {
            'prompt': prompt,
            'generated_bytes': generated_bytes,
            'image_bytes': image_bytes,
            'status_id': status_id,
        }
        await _save_session_data(
            user_session_cache=user_session_cache,
            user_number=user_number,
            session_data=session_data,
        )

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
            viewer_name = (
                contact_info.get('name') if contact_info else None
            )
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
                f'👁️ Status visualizado por {user_number} '
                '(não salvo no DB).'
            )

    except Exception as e:
        logger.error(f'❌ Erro ao processar visualização de status: {e}')
        logger.exception('Detalhes do erro:')


def _is_status_delivery_ack(data: dict) -> bool:
    """Verifica se é ACK de entrega de status (não read)."""
    return (
        data.get('event') == 'message.ack'
        and data.get('payload', {}).get('chat_id') == 'status@broadcast'
        and data.get('payload', {}).get('receipt_type') != 'read'
    )


def _is_duplicate_message(data: dict, message_cache: MessageCache) -> bool:
    """Verifica se a mensagem já foi processada."""
    message_id = data.get('message', {}).get('id')
    return message_id and message_cache.is_message_processed(message_id)


def _get_ignore_reason(data: dict, prompt_cached: str | None) -> str | None:
    """Determina o motivo para ignorar o webhook."""
    event = data.get('event', '')
    action = data.get('action', '')

    reason = None
    if event == 'message.ack':
        reason = 'message.ack'
    elif event in {
        'message.revoke',
        'group.join',
        'group.leave',
        'user.status',
    }:
        reason = event
    elif action in {'message_edited', 'message_deleted'}:
        reason = action
    elif 'message' not in data and 'image' not in data:
        reason = 'no_content'
    elif not prompt_cached:
        reason = 'no_prompt'
    elif prompt_cached and any(
        prompt_cached.startswith(prefix)
        for prefix in [
            'Sua imagem gerada a partir de:',
            'Gerado por Klique AI:',
        ]
    ):
        reason = 'bot_message'
    elif not data.get('sender_id'):
        reason = 'no_sender'
    return reason


async def should_ignore_webhook(
    data: dict, message_cache: MessageCache
) -> tuple[bool, str]:
    """Verifica se o webhook deve ser ignorado e retorna (ignorar, motivo)"""

    if _is_status_delivery_ack(data):
        logger.debug('📨 ACK de entrega de status (não read) - ignorando')
        return True, 'status_delivery_ack'

    prompt_cached, _ = extract_prompt(data)

    # Verifica se a mensagem já foi processada (usando cache MongoDB)
    message_id = data.get('message', {}).get('id')
    if message_id and await message_cache.is_message_processed(message_id):
        logger.debug(f'🔄 Mensagem duplicata (ID: {message_id})')
        return True, 'duplicate'

    reason = _get_ignore_reason(data, prompt_cached)
    if reason:
        logger.debug(f'⏭️ Webhook ignorado: {reason}')
        return True, reason

    return False, ''


# ----------------------------- Command Operations ----------------------------

NO_SESSION_FALLBACK = (
    'Nenhuma imagem anterior encontrada. Envie: imagem <prompt>'
)


async def _handle_imagem_command(
    command_data: dict,
    gemini_service: GeminiService,
    whatsapp_service: WhatsAppService,
    user_session_cache,
):
    """Handler para comando 'imagem'."""
    argument = command_data.get('argument', '')
    sender = command_data.get('sender')
    original_payload = command_data.get('original_payload', {})
    user_number = command_data.get('user_number')

    if not argument:
        await whatsapp_service.send_message(
            phone_number=sender,
            message='Uso: imagem <prompt>. Ex: imagem gato astronauta neon',
        )
        return

    media_path = original_payload.get('image', {}).get('media_path')
    base_image_bytes = None
    if media_path:
        base_image_bytes = await whatsapp_service.download_media(media_path)

    prompt = argument
    generated = await gemini_service.generate_image_from_prompt(
        prompt, base_image_bytes
    )
    if not generated:
        await whatsapp_service.send_message(
            phone_number=sender,
            message=(
                'Falha ao gerar imagem. Tente ajustar o prompt '
                "ou envie 'ajuda'."
            ),
        )
        return

    # Envia ao chat
    await whatsapp_service.send_image_message(
        phone_number=sender,
        image_bytes=generated,
        caption=f'Imagem gerada: {prompt}',
    )

    # Posta status
    status_id = await whatsapp_service.post_status_update(
        image_bytes=generated,
        caption=f'Prompt: {prompt}',
    )

    # Atualiza sessão
    await user_session_cache.save_prompt(user_number, prompt)
    await user_session_cache.save_generated_image(user_number, generated)
    if base_image_bytes:
        await user_session_cache.save_base_image(
            user_number, base_image_bytes
        )
    if status_id:
        await user_session_cache.save_status_id(user_number, status_id)

    logger.success(f'✅ Comando imagem concluído user={user_number}')


async def _handle_legenda_command(
    command_data: dict,
    whatsapp_service: WhatsAppService,
    user_session_cache,
):
    """Handler para comando 'legenda'."""
    argument = command_data.get('argument', '')
    sender = command_data.get('sender')
    user_number = command_data.get('user_number')

    if not argument:
        await whatsapp_service.send_message(
            phone_number=sender,
            message='Uso: legenda <novo texto>',
        )
        return

    existing_image = await user_session_cache.get_generated_image(user_number)
    if not existing_image:
        await whatsapp_service.send_message(
            phone_number=sender, message=NO_SESSION_FALLBACK
        )
        return

    # Deleta status antigo se houver
    last_status_id = await user_session_cache.get_status_id(user_number)
    if last_status_id:
        await whatsapp_service.delete_status(last_status_id)

    # Reposta status com nova legenda
    new_status_id = await whatsapp_service.post_status_update(
        image_bytes=existing_image, caption=argument
    )
    if new_status_id:
        await user_session_cache.save_status_id(user_number, new_status_id)

    await whatsapp_service.send_message(
        phone_number=sender,
        message=f'✅ Legenda atualizada: {argument}',
    )
    logger.success(f'📝 Legenda atualizada user={user_number}')


async def _handle_refazer_command(
    command_data: dict,
    gemini_service: GeminiService,
    whatsapp_service: WhatsAppService,
    user_session_cache,
):
    """Handler para comando 'refazer'."""
    sender = command_data.get('sender')
    user_number = command_data.get('user_number')

    last_prompt = await user_session_cache.get_prompt(user_number)
    if not last_prompt:
        await whatsapp_service.send_message(
            phone_number=sender, message=NO_SESSION_FALLBACK
        )
        return

    base_bytes = await user_session_cache.get_base_image(user_number)
    if not base_bytes:
        base_bytes = await user_session_cache.get_generated_image(user_number)

    generated = await gemini_service.generate_image_from_prompt(
        last_prompt, base_bytes
    )
    if not generated:
        await whatsapp_service.send_message(
            phone_number=sender,
            message=(
                'Falha ao regenerar. Ajuste o prompt com '
                "'imagem <novo prompt>'"
            ),
        )
        return

    # Envia e atualiza status
    await whatsapp_service.send_image_message(
        phone_number=sender,
        image_bytes=generated,
        caption=f'Variação gerada: {last_prompt}',
    )
    last_status_id = await user_session_cache.get_status_id(user_number)
    if last_status_id:
        await whatsapp_service.delete_status(last_status_id)
    status_id = await whatsapp_service.post_status_update(
        image_bytes=generated, caption=f'Variação: {last_prompt}'
    )

    await user_session_cache.save_generated_image(user_number, generated)
    if status_id:
        await user_session_cache.save_status_id(user_number, status_id)

    await whatsapp_service.send_message(
        phone_number=sender, message='✅ Variação pronta.'
    )
    logger.success(f'🔁 Refazer concluído user={user_number}')


async def _handle_editar_command(
    command_data: dict,
    gemini_service: GeminiService,
    whatsapp_service: WhatsAppService,
    user_session_cache,
):
    """Handler para comando 'editar'."""
    argument = command_data.get('argument', '')
    sender = command_data.get('sender')
    user_number = command_data.get('user_number')

    if not argument:
        await whatsapp_service.send_message(
            phone_number=sender,
            message=(
                'Uso: editar <instruções>. Ex: editar adicionar brilho roxo'
            ),
        )
        return

    last_prompt = await user_session_cache.get_prompt(user_number)
    generated_image = (
        await user_session_cache.get_generated_image(user_number)
    )

    if not generated_image:
        await whatsapp_service.send_message(
            phone_number=sender, message=NO_SESSION_FALLBACK
        )
        return

    combined_prompt = (
        f'{last_prompt}. Instruções adicionais: {argument}'
        if last_prompt
        else argument
    )

    edited = await gemini_service.generate_image_from_prompt(
        combined_prompt, generated_image
    )
    if not edited:
        await whatsapp_service.send_message(
            phone_number=sender,
            message=(
                "Falha ao editar. Refine as instruções ou tente 'refazer'."
            ),
        )
        return

    await whatsapp_service.send_image_message(
        phone_number=sender,
        image_bytes=edited,
        caption=f'Edição: {argument}',
    )

    last_status_id = await user_session_cache.get_status_id(user_number)
    if last_status_id:
        await whatsapp_service.delete_status(last_status_id)

    status_id = await whatsapp_service.post_status_update(
        image_bytes=edited,
        caption=f'Edição aplicada: {argument}',
    )

    await user_session_cache.save_generated_image(user_number, edited)
    await user_session_cache.save_prompt(user_number, combined_prompt)
    if status_id:
        await user_session_cache.save_status_id(user_number, status_id)

    await whatsapp_service.send_message(
        phone_number=sender,
        message='✅ Edição concluída.',
    )
    logger.success(f'✏️ Edição concluída user={user_number}')


async def process_command_operation(
    command_data: dict,
    gemini_service: GeminiService,
    whatsapp_service: WhatsAppService,
    user_session_cache,
    status_image_cache: StatusImageCache,
):
    """
    Processa comandos (imagem, legenda, refazer, editar) em background.
    """
    operation = command_data.get('operation')
    sender = command_data.get('sender')
    raw_text = command_data.get('raw_text', '')
    user_number = command_data.get('user_number')

    logger.info(
        f'⚙️ Iniciando processamento de comando {operation} '
        f"user={user_number} raw='{raw_text}'"
    )

    try:
        # HELP nunca chega aqui (tratado inline)
        if operation == 'imagem':
            await _handle_imagem_command(
                command_data,
                gemini_service,
                whatsapp_service,
                user_session_cache,
            )
            return

        if operation == 'legenda':
            await _handle_legenda_command(
                command_data, whatsapp_service, user_session_cache
            )
            return

        if operation == 'refazer':
            await _handle_refazer_command(
                command_data,
                gemini_service,
                whatsapp_service,
                user_session_cache,
            )
            return

        if operation == 'editar':
            await _handle_editar_command(
                command_data,
                gemini_service,
                whatsapp_service,
                user_session_cache,
            )
            return

        logger.warning(f'⚠️ Operação desconhecida: {operation}')

    except Exception as e:
        logger.error(
            f'❌ Erro ao processar comando {operation} user={user_number}: {e}'
        )
        try:
            await whatsapp_service.send_message(
                phone_number=sender,
                message='Erro interno no processamento do comando.',
            )
        except Exception:  # noqa: BLE001
            pass


def _handle_status_view(
    data: dict,
    background_tasks: BackgroundTasks,
    deps: WebhookDependencies,
) -> dict | None:
    """Trata eventos de visualização de status."""
    is_ack_read = (
        data.get('event') == 'message.ack'
        and data.get('payload', {}).get('chat_id') == 'status@broadcast'
        and data.get('payload', {}).get('receipt_type') == 'read'
    )

    if is_ack_read or data.get('event') == 'status.viewed':
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
    return None


async def _handle_command(
    data: dict,
    cmd_ctx,
    background_tasks: BackgroundTasks,
    deps: WebhookDependencies,
) -> dict | None:
    """Trata comandos recebidos."""
    sender = data.get('sender_id')
    if not sender:
        return {
            'status': 'ignored',
            'detail': 'command_without_sender',
        }

    # AJUDA: responde imediatamente
    if cmd_ctx.operation == CommandOperation.AJUDA:
        await deps.whatsapp_service.send_message(
            phone_number=sender, message=HELP_MESSAGE
        )
        return {
            'status': 'accepted',
            'detail': 'help_sent',
            'command': cmd_ctx.operation.name.lower(),
        }

    # Mapeia operação
    op_map = {
        CommandOperation.IMAGEM: 'imagem',
        CommandOperation.LEGENDA: 'legenda',
        CommandOperation.REFAZER: 'refazer',
        CommandOperation.EDITAR: 'editar',
    }
    operation_str = op_map.get(cmd_ctx.operation)

    # Feedback imediato
    await deps.whatsapp_service.send_message(
        phone_number=sender,
        message=f'⚙️ Processando comando {operation_str}...',
    )

    command_data = {
        'operation': operation_str,
        'argument': cmd_ctx.argument,
        'sender': sender,
        'raw_text': cmd_ctx.raw_text,
        'original_payload': data,
        'user_number': extract_primary_user_number(data),
    }

    background_tasks.add_task(
        process_command_operation,
        command_data,
        deps.gemini_service,
        deps.whatsapp_service,
        deps.user_session_cache,
        deps.status_image_cache,
    )

    return {
        'status': 'accepted',
        'detail': 'command_queued',
        'command': operation_str,
    }


async def _handle_normal_message(
    data: dict,
    background_tasks: BackgroundTasks,
    deps: WebhookDependencies,
) -> dict:
    """Trata mensagens normais (não comandos nem status)."""
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
        deps.user_session_cache,
        deps.status_image_cache,
    )

    return {
        'status': 'accepted',
        'detail': 'Webhook agendado para processamento',
    }


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

        # ------------------------------ Status view handling -----------------
        status_result = _handle_status_view(data, background_tasks, deps)
        if status_result:
            return status_result

        # ------------------------------ Command parsing (V1) -----------------
        message_text = data.get('message', {}).get('text')
        cmd_ctx = parse_command(message_text)

        if cmd_ctx:
            command_result = await _handle_command(
                data, cmd_ctx, background_tasks, deps
            )
            if command_result:
                return command_result

        # ----------------------------- Normal message flow -------------------
        return await _handle_normal_message(data, background_tasks, deps)

    except Exception as e:
        logger.error(f'❌ Erro no webhook: {str(e)}')
        logger.exception('Detalhes do erro no webhook:')
        return {'status': 'error', 'detail': str(e)}
    finally:
        logger.debug('🔌 Webhook principal finalizado')
