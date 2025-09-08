from datetime import datetime  # noqa: I001

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorCollection
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..routers import schemas
from ..services.protocols import ImageGenerationServiceProtocol
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


async def process_status_viewed_for_image_generation(
    data: dict,
    image_generation_service: ImageGenerationServiceProtocol,
    whatsapp_service: WhatsAppService,
    db: AsyncIOMotorDatabase,
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

        status_images_collection = db.get_collection('status_images')
        last_status = await status_images_collection.find_one(
            {}, sort=[('created_at', -1)]
        )
        cached_image_bytes = (
            bytes(last_status['image_bytes']) if last_status else None
        )

        if cached_image_bytes:
            prompt = (
                f"Edite esta imagem adicionando o texto '{viewer_name}' "
                f'de forma criativa e elegante. Mantenha o estilo '
                f'original da imagem.'
            )
            logger.info(
                f'🎨 Editando imagem anterior em cache para {viewer_name}...'
            )

            new_image_bytes = await image_generation_service.generate_content(
                prompt, cached_image_bytes
            )
        else:
            logger.info(
                '❕ Nenhuma imagem em cache para gerar variação de status. '
                'Processo interrompido.'
            )
            return

        if not new_image_bytes:
            logger.warning('⚠️ Gemini não conseguiu gerar nova imagem')
            return

        logger.success('✅ Nova imagem gerada! Postando no status...')

        # Deleta o status antigo, se existir
        last_status_id = last_status.get('status_id') if last_status else None
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


async def process_status_view(
    data: dict, status_views_collection: AsyncIOMotorCollection
) -> None:
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


# ----------------------------- Command Operations ----------------------------

NO_SESSION_FALLBACK = (
    'Nenhuma imagem anterior encontrada. Envie: imagem <prompt>'
)


async def _handle_imagem_command(
    command_data: dict,
    image_generation_service: ImageGenerationServiceProtocol,
    whatsapp_service: WhatsAppService,
    db: AsyncIOMotorDatabase,
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
    generated = await image_generation_service.generate_content(
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
    user_sessions = db.get_collection('user_sessions')
    update_data = {
        'last_prompt': prompt,
        'last_generated_image': generated,
        'updated_at': datetime.utcnow(),
    }
    if base_image_bytes:
        update_data['last_base_image'] = base_image_bytes
    if status_id:
        update_data['last_status_id'] = status_id

    await user_sessions.update_one(
        {'user_number': user_number},
        {'$set': update_data},
        upsert=True,
    )

    logger.success(f'✅ Comando imagem concluído user={user_number}')


async def _handle_legenda_command(
    command_data: dict,
    whatsapp_service: WhatsAppService,
    db: AsyncIOMotorDatabase,
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

    user_sessions = db.get_collection('user_sessions')
    session = await user_sessions.find_one({'user_number': user_number})
    existing_image = (
        bytes(session['last_generated_image'])
        if session and 'last_generated_image' in session
        else None
    )
    if not existing_image:
        await whatsapp_service.send_message(
            phone_number=sender, message=NO_SESSION_FALLBACK
        )
        return

    # Deleta status antigo se houver
    last_status_id = session.get('last_status_id') if session else None
    if last_status_id:
        await whatsapp_service.delete_status(last_status_id)

    # Reposta status com nova legenda
    new_status_id = await whatsapp_service.post_status_update(
        image_bytes=existing_image, caption=argument
    )
    if new_status_id:
        await user_sessions.update_one(
            {'user_number': user_number},
            {'$set': {'last_status_id': new_status_id}},
        )

    await whatsapp_service.send_message(
        phone_number=sender,
        message=f'✅ Legenda atualizada: {argument}',
    )
    logger.success(f'📝 Legenda atualizada user={user_number}')


async def _handle_refazer_command(
    command_data: dict,
    image_generation_service: ImageGenerationServiceProtocol,
    whatsapp_service: WhatsAppService,
    db: AsyncIOMotorDatabase,
):
    """Handler para comando 'refazer'."""
    sender = command_data.get('sender')
    user_number = command_data.get('user_number')

    user_sessions = db.get_collection('user_sessions')
    session = await user_sessions.find_one({'user_number': user_number})
    if not session or 'last_prompt' not in session:
        await whatsapp_service.send_message(
            phone_number=sender, message=NO_SESSION_FALLBACK
        )
        return
    last_prompt = session['last_prompt']

    base_bytes = (
        bytes(session['last_base_image'])
        if 'last_base_image' in session
        else bytes(session.get('last_generated_image'))
    )

    generated = await image_generation_service.generate_content(
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
    last_status_id = session.get('last_status_id')
    if last_status_id:
        await whatsapp_service.delete_status(last_status_id)
    status_id = await whatsapp_service.post_status_update(
        image_bytes=generated, caption=f'Variação: {last_prompt}'
    )

    await user_sessions.update_one(
        {'user_number': user_number},
        {
            '$set': {
                'last_generated_image': generated,
                'last_status_id': status_id,
            }
        },
    )

    await whatsapp_service.send_message(
        phone_number=sender, message='✅ Variação pronta.'
    )
    logger.success(f'🔁 Refazer concluído user={user_number}')


async def _handle_editar_command(
    command_data: dict,
    image_generation_service: ImageGenerationServiceProtocol,
    whatsapp_service: WhatsAppService,
    db: AsyncIOMotorDatabase,
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

    user_sessions = db.get_collection('user_sessions')
    session = await user_sessions.find_one({'user_number': user_number})
    if not session or 'last_generated_image' not in session:
        await whatsapp_service.send_message(
            phone_number=sender, message=NO_SESSION_FALLBACK
        )
        return
    last_prompt = session.get('last_prompt')
    generated_image = bytes(session['last_generated_image'])

    combined_prompt = (
        f'{last_prompt}. Instruções adicionais: {argument}'
        if last_prompt
        else argument
    )

    edited = await image_generation_service.generate_content(
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

    last_status_id = session.get('last_status_id')
    if last_status_id:
        await whatsapp_service.delete_status(last_status_id)

    status_id = await whatsapp_service.post_status_update(
        image_bytes=edited,
        caption=f'Edição aplicada: {argument}',
    )

    await user_sessions.update_one(
        {'user_number': user_number},
        {
            '$set': {
                'last_generated_image': edited,
                'last_prompt': combined_prompt,
                'last_status_id': status_id,
            }
        },
    )

    await whatsapp_service.send_message(
        phone_number=sender,
        message='✅ Edição concluída.',
    )
    logger.success(f'✏️ Edição concluída user={user_number}')


async def process_command_operation(
    command_data: dict,
    image_generation_service: ImageGenerationServiceProtocol,
    whatsapp_service: WhatsAppService,
    db: AsyncIOMotorDatabase,
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
                image_generation_service,
                whatsapp_service,
                db,
            )
            return

        if operation == 'legenda':
            await _handle_legenda_command(command_data, whatsapp_service, db)
            return

        if operation == 'refazer':
            await _handle_refazer_command(
                command_data,
                image_generation_service,
                whatsapp_service,
                db,
            )
            return

        if operation == 'editar':
            await _handle_editar_command(
                command_data,
                image_generation_service,
                whatsapp_service,
                db,
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
        background_tasks.add_task(
            process_status_view, data, deps.db.get_collection('status_views')
        )
        background_tasks.add_task(
            process_status_viewed_for_image_generation,
            data,
            deps.image_generation_service,
            deps.whatsapp_service,
            deps.db,
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
        deps.image_generation_service,
        deps.whatsapp_service,
        deps.db,
    )

    return {
        'status': 'accepted',
        'detail': 'command_queued',
        'command': operation_str,
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
        contact_info = await deps.whatsapp_service.get_contact_info(
            phone_number=user_number
        )

        logger.bind(payload=data).info(
            f'Contato: {contact_info} recebeu sua mensagem'
        )

        # --------------------- Fluxo 1: Status view handling -----------------
        status_result = _handle_status_view(data, background_tasks, deps)
        if status_result:
            return status_result

        # --------------------- Fluxo 2: Command parsing (V1) -----------------
        message_text = data.get('message', {}).get('text')
        cmd_ctx = parse_command(message_text)

        if cmd_ctx:
            command_result = await _handle_command(
                data, cmd_ctx, background_tasks, deps
            )
            if command_result:
                return command_result

        # ----------------------------- Normal message flow (REMOVED) ---------
        # O fluxo de mensagens normais foi removido.
        # Apenas comandos explícitos são processados.
        logger.debug(
            'Nenhum comando ou evento de status detectado. Ignorando.'
        )
        return {'status': 'ok', 'reason': 'no_command_or_event'}

    except Exception as e:
        logger.error(f'❌ Erro no webhook: {str(e)}')
        logger.exception('Detalhes do erro no webhook:')
        return {'status': 'error', 'detail': str(e)}
    finally:
        logger.debug('🔌 Webhook principal finalizado')
