from datetime import datetime  # noqa: I001
from typing import Any
from dataclasses import dataclass

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorCollection
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..routers import schemas
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


@dataclass
class SessionUpdateData:
    """Dados para atualização de sessão do usuário."""

    user_number: str
    prompt: str
    generated_bytes: bytes
    base_images_bytes: list[bytes] = None
    status_id: str = None


@dataclass
class EditProcessData:
    """Dados para processamento de edições."""

    generation_result: list[bytes]
    argument: str
    sender: str
    user_number: str
    session: dict | None


@dataclass
class EditStatusUpdateData:
    """Dados para atualização de status e sessão após edição."""

    edited_bytes: bytes
    combined_prompt: str
    argument: str
    user_number: str
    session: dict | None


router = APIRouter(
    prefix='/webhooks',
    tags=['webhooks'],
)


async def process_status_viewed_for_image_generation(
    data: dict,
    image_generation_service: Any,
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

            # Como este fluxo não é iniciado por um usuário específico,
            # ele não pode usar uma sessão de usuário.
            # Vamos criar um chat temporário para esta operação.
            temp_chat = await image_generation_service.get_or_create_chat(
                f'status_viewer_{user_number}'
            )
            generation_result = (
                await image_generation_service.generate_content_from_chat(
                    prompt, temp_chat, [cached_image_bytes]
                )
            )
            new_image_bytes = (
                generation_result[0] if generation_result else None
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


def _extract_media_paths(payload: dict) -> list[str]:
    """Extrai caminhos de mídia do payload."""
    media_paths = []

    if 'image' in payload:
        media_path = payload.get('image', {}).get('media_path')
        if media_path:
            media_paths.append(media_path)
    elif 'media' in payload and isinstance(payload['media'], list):
        for media_item in payload['media']:
            if media_item.get('type') == 'image' and media_item.get(
                'media_path'
            ):
                media_paths.append(media_item['media_path'])

    return media_paths


async def _download_media_files(
    whatsapp_service: WhatsAppService, media_paths: list[str]
) -> list[bytes]:
    """Faz download dos arquivos de mídia."""
    base_images_bytes = []
    if not media_paths:
        return base_images_bytes

    logger.info(f'Baixando {len(media_paths)} imagens de entrada...')
    for path in media_paths:
        try:
            image_bytes = await whatsapp_service.download_media(path)
            if image_bytes:
                base_images_bytes.append(image_bytes)
        except Exception as e:
            logger.warning(f'Falha ao baixar mídia de {path}: {e}')

    return base_images_bytes


async def _update_user_session(
    db: AsyncIOMotorDatabase,
    data: SessionUpdateData,
) -> None:
    """Atualiza a sessão do usuário no banco."""
    user_sessions = db.get_collection('user_sessions')
    update_data = {
        'last_prompt': data.prompt,
        'last_generated_image': data.generated_bytes,
        'updated_at': datetime.utcnow(),
    }
    if data.base_images_bytes:
        update_data['last_base_image'] = data.base_images_bytes[0]
    if data.status_id:
        update_data['last_status_id'] = data.status_id

    await user_sessions.update_one(
        {'user_number': data.user_number},
        {'$set': update_data},
        upsert=True,
    )


async def _update_status_cache(
    db: AsyncIOMotorDatabase,
    generated_bytes: bytes,
    prompt: str,
    status_id: str = None,
) -> None:
    """Atualiza o cache de status para variações automáticas."""
    status_images_collection = db.get_collection('status_images')
    await status_images_collection.replace_one(
        {},  # Filter vazio para substituir sempre o documento mais recente
        {
            'image_bytes': generated_bytes,
            'prompt': prompt,
            'status_id': status_id,
            'created_at': datetime.utcnow(),
        },
        upsert=True,
    )


async def _handle_imagem_command(
    command_data: dict,
    image_generation_service: Any,
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

    # Extrai e baixa imagens de entrada
    media_paths = _extract_media_paths(original_payload)
    base_images_bytes = await _download_media_files(
        whatsapp_service, media_paths
    )

    prompt = argument
    chat = await image_generation_service.get_or_create_chat(user_number)
    generation_result = (
        await image_generation_service.generate_content_from_chat(
            prompt, chat, base_images_bytes
        )
    )
    if not generation_result:
        await whatsapp_service.send_message(
            phone_number=sender,
            message=(
                'Falha ao gerar imagem. Tente ajustar o prompt '
                "ou envie 'ajuda'."
            ),
        )
        return

    # O comando imagem sempre espera uma única imagem
    generated_bytes = generation_result[0]

    # Envia ao chat
    await whatsapp_service.send_image_message(
        phone_number=sender,
        image_bytes=generated_bytes,
        caption=f'Imagem gerada: {prompt}',
    )

    # Posta status
    status_id = await whatsapp_service.post_status_update(
        image_bytes=generated_bytes,
        caption=f'Prompt: {prompt}',
    )

    # Atualiza sessão
    session_data = SessionUpdateData(
        user_number=user_number,
        prompt=prompt,
        generated_bytes=generated_bytes,
        base_images_bytes=base_images_bytes,
        status_id=status_id,
    )
    await _update_user_session(db, session_data)

    # Salva a imagem gerada no StatusImageCache para variações automáticas
    await _update_status_cache(db, generated_bytes, prompt, status_id)

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
    image_generation_service: Any,
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

    # Recupera imagem base dos bytes armazenados diretamente
    base_bytes = None
    if 'last_base_image' in session:
        base_bytes = bytes(session['last_base_image'])
    elif 'last_generated_image' in session:
        base_bytes = bytes(session['last_generated_image'])

    chat = await image_generation_service.get_or_create_chat(user_number)
    generation_result = (
        await image_generation_service.generate_content_from_chat(
            last_prompt, chat, [base_bytes] if base_bytes else None
        )
    )
    if not generation_result:
        await whatsapp_service.send_message(
            phone_number=sender,
            message=(
                'Falha ao regenerar. Ajuste o prompt com '
                "'imagem <novo prompt>'"
            ),
        )
        return

    generated_bytes = generation_result[0]

    # Envia e atualiza status
    await whatsapp_service.send_image_message(
        phone_number=sender,
        image_bytes=generated_bytes,
        caption=f'Variação gerada: {last_prompt}',
    )
    last_status_id = session.get('last_status_id') if session else None
    if last_status_id:
        await whatsapp_service.delete_status(last_status_id)
    status_id = await whatsapp_service.post_status_update(
        image_bytes=generated_bytes, caption=f'Variação: {last_prompt}'
    )

    await user_sessions.update_one(
        {'user_number': user_number},
        {
            '$set': {
                'last_generated_image': generated_bytes,
                'last_status_id': status_id,
            }
        },
    )

    # Atualiza o StatusImageCache para variações automáticas
    status_images_collection = db.get_collection('status_images')
    await status_images_collection.replace_one(
        {},  # Filter vazio para substituir sempre o documento mais recente
        {
            'image_bytes': generated_bytes,
            'prompt': last_prompt,
            'status_id': status_id,
            'created_at': datetime.utcnow(),
        },
        upsert=True,
    )

    await whatsapp_service.send_message(
        phone_number=sender, message='✅ Variação pronta.'
    )
    logger.success(f'🔁 Refazer concluído user={user_number}')


async def _get_images_for_editing(
    session: dict | None,
    whatsapp_service: WhatsAppService,
    original_payload: dict,
) -> list[bytes]:
    """Obtém imagens para edição da sessão ou payload atual."""
    images_for_editing = []

    # Adiciona última imagem gerada da sessão
    if session and 'last_generated_image' in session:
        try:
            image_bytes = bytes(session['last_generated_image'])
            images_for_editing.append(image_bytes)
        except Exception as e:
            logger.warning('Falha ao ler imagem da sessão: %s', e)

    # Adiciona novas imagens do payload
    media_paths = _extract_media_paths(original_payload)
    new_images = await _download_media_files(whatsapp_service, media_paths)
    images_for_editing.extend(new_images)

    return images_for_editing


async def _process_edited_images(
    data: EditProcessData,
    whatsapp_service: WhatsAppService,
    db: AsyncIOMotorDatabase,
) -> None:
    """Processa e envia imagens editadas."""
    for i, edited_bytes in enumerate(data.generation_result):
        caption = (
            f'Edição: {data.argument}'
            if len(data.generation_result) == 1
            else f'Edição: {data.argument} ({i + 1}'
            f'/{len(data.generation_result)})'
        )
        await whatsapp_service.send_image_message(
            phone_number=data.sender,
            image_bytes=edited_bytes,
            caption=caption,
        )

        # Apenas a primeira imagem atualiza o status principal e a sessão
        if i == 0:
            combined_prompt = f'Edite esta imagem: {data.argument}'
            update_data = EditStatusUpdateData(
                edited_bytes=edited_bytes,
                combined_prompt=combined_prompt,
                argument=data.argument,
                user_number=data.user_number,
                session=data.session,
            )
            await _update_status_and_session_for_edit(
                update_data, whatsapp_service, db
            )


async def _update_status_and_session_for_edit(
    data: EditStatusUpdateData,
    whatsapp_service: WhatsAppService,
    db: AsyncIOMotorDatabase,
) -> None:
    """Atualiza status e sessão após edição."""
    # Remove status antigo
    if data.session:
        last_status_id = data.session.get('last_status_id')
        if last_status_id:
            await whatsapp_service.delete_status(last_status_id)

    # Cria novo status
    status_id = await whatsapp_service.post_status_update(
        image_bytes=data.edited_bytes,
        caption=f'Edição aplicada: {data.argument}',
    )

    # Atualiza sessão do usuário
    user_sessions = db.get_collection('user_sessions')
    await user_sessions.update_one(
        {'user_number': data.user_number},
        {
            '$set': {
                'last_generated_image': data.edited_bytes,
                'last_prompt': data.combined_prompt,
                'last_status_id': status_id,
            }
        },
    )

    # Atualiza cache de status
    await _update_status_cache(
        db, data.edited_bytes, data.combined_prompt, status_id
    )


async def _handle_editar_command(
    command_data: dict,
    image_generation_service: Any,
    whatsapp_service: WhatsAppService,
    db: AsyncIOMotorDatabase,
):
    """Handler para comando 'editar'."""
    argument = command_data.get('argument', '')
    sender = command_data.get('sender')
    original_payload = command_data.get('original_payload', {})
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

    images_for_editing = await _get_images_for_editing(
        session, whatsapp_service, original_payload
    )

    if not images_for_editing:
        await whatsapp_service.send_message(
            phone_number=sender,
            message='Nenhuma imagem encontrada para editar.'
            ' Envie uma imagem ou use o comando `imagem` primeiro.',
        )
        return

    combined_prompt = f'Edite esta imagem: {argument}'
    chat = await image_generation_service.get_or_create_chat(user_number)
    generation_result = (
        await image_generation_service.generate_content_from_chat(
            combined_prompt, chat, images_for_editing
        )
    )

    if not generation_result:
        await whatsapp_service.send_message(
            phone_number=sender,
            message=(
                "Falha ao editar. Refine as instruções ou tente 'refazer'."
            ),
        )
        return

    edit_data = EditProcessData(
        generation_result=generation_result,
        argument=argument,
        sender=sender,
        user_number=user_number,
        session=session,
    )
    await _process_edited_images(edit_data, whatsapp_service, db)

    await whatsapp_service.send_message(
        phone_number=sender,
        message='✅ Edição concluída.',
    )
    logger.success(f'✏️ Edição concluída user={user_number}')


async def process_command_operation(
    command_data: dict,
    image_generation_service: Any,
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
        logger.exception('Detalhes do erro no processamento do comando:')
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
        logger.bind(payload=data).info(f'🔔 Webhook recebido: {data}')
        logger.bind(payload=data).info(
            f'Contato: {contact_info} recebeu sua mensagem'
        )

        # --------------------- Fluxo 1: Status view handling -----------------
        status_result = _handle_status_view(data, background_tasks, deps)
        if status_result:
            return status_result

        # --------------------- Fluxo 2: Command parsing (V1) -----------------
        message_body = data.get('message', {})
        image_body = data.get('image', {})
        message_text = (
            message_body.get('text')
            or message_body.get('caption')
            or image_body.get('caption')
        )
        logger.debug(f"Texto extraído para parsing: '{message_text}'")
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
