from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from ..command import HELP_MESSAGE, CommandOperation, parse_command
from ..routers import schemas
from ..services.whatsapp import WhatsAppService
from ..utils import extract_primary_user_number, extract_user_number
from ..webhook_dependencies import (
    WebhookDependencies,
    get_webhook_dependencies,
)


@dataclass
class SessionUpdateData:
    """Dados para atualização de sessão do usuário."""

    user_number: str
    prompt: str
    generated_bytes: bytes
    base_images_bytes: list[bytes] = None
    status_id: str = None


router = APIRouter(prefix='/webhooks', tags=['webhooks'])

NO_SESSION_FALLBACK = (
    'Nenhuma imagem anterior encontrada. Envie: imagem <prompt>'
)


async def _check_rate_limit(db: AsyncIOMotorDatabase) -> bool:
    """Verifica rate limit para geração de status (1 por minuto)."""
    try:
        collection = db.get_collection('status_generation_rate_limit')
        now = datetime.utcnow()
        one_minute_ago = now - timedelta(minutes=1)

        last_generation = await collection.find_one(
            {}, sort=[('created_at', -1)]
        )

        if (
            not last_generation
            or last_generation['created_at'] < one_minute_ago
        ):
            await collection.insert_one({
                'created_at': now,
                'type': 'status_view_generation',
            })
            await collection.delete_many({
                'created_at': {'$lt': now - timedelta(minutes=5)}
            })
            logger.info('✅ Rate limit OK - Geração permitida')
            return True

        time_remaining = (
            60 - (now - last_generation['created_at']).total_seconds()
        )
        logger.info(
            f'⏳ Rate limit ativo - Próxima geração em {time_remaining:.0f}s'
        )
        return False
    except Exception as e:
        logger.error(f'❌ Erro ao verificar rate limit: {e}')
        return True


async def _manage_recent_viewers(
    db: AsyncIOMotorDatabase, viewer_name: str, user_number: str
) -> list[str]:
    """Gerencia lista de visualizadores recentes (últimos 2 minutos)."""
    try:
        collection = db.get_collection('status_recent_viewers')
        two_minutes_ago = datetime.utcnow() - timedelta(minutes=2)

        # Adiciona viewer atual
        await collection.insert_one({
            'viewer_name': viewer_name,
            'user_number': user_number,
            'viewed_at': datetime.utcnow(),
        })

        # Busca viewers recentes
        recent_viewers = await collection.find({
            'viewed_at': {'$gte': two_minutes_ago}
        }).to_list(length=None)

        viewer_names = [viewer['viewer_name'] for viewer in recent_viewers]

        # Limpa registros antigos
        await collection.delete_many({'viewed_at': {'$lt': two_minutes_ago}})

        return viewer_names
    except Exception as e:
        logger.error(f'❌ Erro ao gerenciar viewers recentes: {e}')
        return [viewer_name]


def _format_viewers_text(viewers: list[str], max_names: int = 3) -> str:
    """Formata texto de visualizadores com limite."""
    if len(viewers) <= max_names:
        return ', '.join(viewers)
    return (
        f'{", ".join(viewers[:max_names])} e mais {len(viewers) - max_names}'
    )


async def _generate_status_caption(
    image_generation_service: Any,
    prompt: str,
    user_name: str = None,
    chat=None,
) -> str:
    """Gera legenda criativa ou retorna fallback."""
    try:
        if hasattr(image_generation_service, 'generate_status_caption'):
            caption = await image_generation_service.generate_status_caption(
                chat=chat, image_prompt=prompt, user_name=user_name
            )
            if caption:
                logger.info(f'Legenda criativa gerada: "{caption}"')
                return caption
    except Exception as e:
        logger.warning(f'Erro ao gerar legenda criativa: {e}')

    logger.debug('Usando legenda padrão como fallback')
    return (
        f'Prompt: {prompt}'
        if not prompt.startswith(('Visualizado por', 'Edição', 'Variação'))
        else prompt
    )


async def process_status_viewed_for_image_generation(
    data: dict,
    image_generation_service: Any,
    whatsapp_service: WhatsAppService,
    db: AsyncIOMotorDatabase,
) -> None:
    """Gera nova imagem quando alguém visualiza status."""
    try:
        sender_id = data.get('payload', {}).get('sender_id')
        if not sender_id:
            logger.warning(
                '❌ Sender ID não encontrado na visualização de status'
            )
            return

        user_number = extract_user_number(sender_id)

        # Obtém nome do visualizador
        viewer_name = None
        try:
            contact_info = await whatsapp_service.get_contact_info(user_number)
            viewer_name = contact_info.get('name') if contact_info else None
        except Exception:
            pass

        if not viewer_name:
            viewer_name = f'*{user_number[-4:]}'

        logger.info(f'👁️ Status visualizado por {viewer_name} ({user_number})')

        # Verifica rate limiting
        if not await _check_rate_limit(db):
            logger.info(f'⏸️ Geração pausada por rate limiting - {viewer_name}')
            return

        # Gerencia visualizadores recentes
        recent_viewers = await _manage_recent_viewers(
            db, viewer_name, user_number
        )

        # Busca imagem em cache
        status_images = db.get_collection('status_images')
        last_status = await status_images.find_one(
            {}, sort=[('created_at', -1)]
        )

        if not last_status:
            logger.info('❕ Nenhuma imagem em cache. Processo interrompido.')
            return

        cached_image_bytes = bytes(last_status['image_bytes'])

        # Cria prompt baseado no número de visualizadores
        if len(recent_viewers) == 1:
            prompt = (
                f'Edite esta imagem adicionando o texto '
                f"'{recent_viewers[0]}' de forma criativa e elegante."
                ' Mantenha o estilo original.'
            )
            viewer_prompt = f'Visualizado por {recent_viewers[0]}'
        else:
            viewers_text = _format_viewers_text(recent_viewers)
            prompt = (
                f"Edite esta imagem adicionando os textos '{viewers_text}'"
                ' de forma criativa e elegante. Mantenha o estilo original.'
            )
            viewer_prompt = f'Visualizado por: {viewers_text}'

        logger.info(
            f'🎨 Editando imagem para {len(recent_viewers)} '
            'visualizador(es)...'
        )

        # Gera nova imagem
        temp_chat = await image_generation_service.get_or_create_chat(
            'status_viewer_batch'
        )
        generation_result = (
            await image_generation_service.generate_content_from_chat(
                prompt, temp_chat, [cached_image_bytes]
            )
        )

        if not generation_result:
            logger.warning('⚠️ Gemini não conseguiu gerar nova imagem')
            return

        new_image_bytes = generation_result[0]
        logger.success('✅ Nova imagem gerada! Postando no status...')

        # Gera legenda e posta status
        status_caption = await _generate_status_caption(
            image_generation_service, viewer_prompt, None, temp_chat
        )

        if not status_caption.startswith('Visualizado por'):
            status_caption = (
                f'Visualizado por: {_format_viewers_text(recent_viewers)} 👁️'
            )

        await _delete_latest_status(whatsapp_service)
        await whatsapp_service.post_status_update(
            new_image_bytes, status_caption
        )

        logger.success(
            f'🎉 Novo status gerado para {len(recent_viewers)}'
            ' visualizador(es)!'
        )

        # Limpa viewers após gerar
        await db.get_collection('status_recent_viewers').delete_many({})

    except Exception as e:
        logger.error(f'❌ Erro ao processar visualização de status: {e}')
        logger.exception('Detalhes do erro:')


async def process_status_view(
    data: dict, status_views_collection: AsyncIOMotorCollection
) -> None:
    """Processa e salva visualização de status no banco."""
    try:
        # Extrai dados do payload
        sender_id = data.get('sender_id') or data.get('payload', {}).get(
            'sender_id'
        )
        timestamp_str = data.get('timestamp') or data.get('payload', {}).get(
            'timestamp'
        )

        if not sender_id or not timestamp_str:
            logger.warning(
                f'❌ Dados incompletos - sender_id: {sender_id},'
                f' timestamp: {timestamp_str}'
            )
            return

        user_number = extract_user_number(sender_id)
        viewed_at = datetime.fromisoformat(
            timestamp_str.replace('Z', '+00:00')
        )

        status_view = schemas.StatusView(
            user_number=user_number, viewed_at=viewed_at
        )

        try:
            await status_views_collection.insert_one(status_view.model_dump())
            logger.info(f'👁️ Status visualizado por {user_number} salvo no DB.')
        except Exception:
            logger.info(
                f'👁️ Status visualizado por {user_number} (não salvo no DB).'
            )

    except Exception as e:
        logger.error(f'❌ Erro ao processar visualização: {e}')


async def _delete_latest_status(whatsapp_service: WhatsAppService) -> None:
    """Deleta o status mais recente."""
    try:
        latest_status_id = await whatsapp_service.get_latest_status_id()
        if latest_status_id:
            logger.info(f'🗑️ Deletando status: {latest_status_id}')
            await whatsapp_service.delete_status(latest_status_id)
        else:
            logger.info('📋 Nenhum status encontrado para deletar')
    except Exception as e:
        logger.warning(f'⚠️ Erro ao deletar status: {e}')


def _extract_media_paths(payload: dict) -> list[str]:
    """Extrai caminhos de mídia do payload."""
    media_paths = []

    # Verifica campo 'image'
    if 'image' in payload:
        media_path = payload.get('image', {}).get('media_path')
        if media_path:
            media_paths.append(media_path)

    # Verifica campo 'media'
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
    if not media_paths:
        return []

    logger.info(f'Baixando {len(media_paths)} imagens...')
    images = []

    for path in media_paths:
        try:
            image_bytes = await whatsapp_service.download_media(path)
            if image_bytes:
                images.append(image_bytes)
        except Exception as e:
            logger.warning(f'Falha ao baixar mídia de {path}: {e}')

    return images


async def _update_user_session(
    db: AsyncIOMotorDatabase, data: SessionUpdateData
) -> None:
    """Atualiza sessão do usuário no banco."""
    collection = db.get_collection('user_sessions')
    update_data = {
        'last_prompt': data.prompt,
        'last_generated_image': data.generated_bytes,
        'updated_at': datetime.utcnow(),
    }

    if data.base_images_bytes:
        update_data['last_base_image'] = data.base_images_bytes[0]
    if data.status_id:
        update_data['last_status_id'] = data.status_id

    await collection.update_one(
        {'user_number': data.user_number},
        {'$set': update_data},
        upsert=True,
    )


async def _update_status_cache(
    db: AsyncIOMotorDatabase,
    image_bytes: bytes,
    prompt: str,
    status_id: str = None,
) -> None:
    """Atualiza cache de status para variações automáticas."""
    collection = db.get_collection('status_images')
    await collection.replace_one(
        {},
        {
            'image_bytes': image_bytes,
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
    user_number = command_data.get('user_number')
    original_payload = command_data.get('original_payload', {})

    if not argument:
        await whatsapp_service.send_message(
            sender, 'Uso: imagem <prompt>. Ex: imagem gato astronauta neon'
        )
        return

    # Processa mídia de entrada
    media_paths = _extract_media_paths(original_payload)
    base_images_bytes = await _download_media_files(
        whatsapp_service, media_paths
    )

    # Gera imagem
    chat = await image_generation_service.get_or_create_chat(user_number)
    generation_result = (
        await image_generation_service.generate_content_from_chat(
            argument, chat, base_images_bytes
        )
    )

    if not generation_result:
        await whatsapp_service.send_message(
            sender,
            "Falha ao gerar imagem. Tente ajustar o prompt ou envie 'ajuda'.",
        )
        return

    generated_bytes = generation_result[0]

    # Envia ao chat
    await whatsapp_service.send_image_message(
        sender, generated_bytes, f'Imagem gerada: {argument}'
    )

    # Gera legenda e posta status
    contact_info = await whatsapp_service.get_contact_info(user_number)
    user_name = contact_info.get('name') if contact_info else None

    status_caption = await _generate_status_caption(
        image_generation_service, argument, user_name, chat
    )
    status_id = await whatsapp_service.post_status_update(
        generated_bytes, status_caption
    )

    # Atualiza dados
    session_data = SessionUpdateData(
        user_number=user_number,
        prompt=argument,
        generated_bytes=generated_bytes,
        base_images_bytes=base_images_bytes,
        status_id=status_id,
    )
    await _update_user_session(db, session_data)
    await _update_status_cache(db, generated_bytes, argument, status_id)

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
            sender, 'Uso: legenda <novo texto>'
        )
        return

    # Busca imagem da sessão
    collection = db.get_collection('user_sessions')
    session = await collection.find_one({'user_number': user_number})

    if not session or 'last_generated_image' not in session:
        await whatsapp_service.send_message(sender, NO_SESSION_FALLBACK)
        return

    existing_image = bytes(session['last_generated_image'])

    # Atualiza status com nova legenda
    await _delete_latest_status(whatsapp_service)
    new_status_id = await whatsapp_service.post_status_update(
        existing_image, argument
    )

    if new_status_id:
        await collection.update_one(
            {'user_number': user_number},
            {'$set': {'last_status_id': new_status_id}},
        )

    await whatsapp_service.send_message(
        sender, f'✅ Legenda atualizada: {argument}'
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

    # Busca sessão
    collection = db.get_collection('user_sessions')
    session = await collection.find_one({'user_number': user_number})

    if not session or 'last_prompt' not in session:
        await whatsapp_service.send_message(sender, NO_SESSION_FALLBACK)
        return

    last_prompt = session['last_prompt']

    # Recupera imagem base
    base_bytes = None
    if 'last_base_image' in session:
        base_bytes = bytes(session['last_base_image'])
    elif 'last_generated_image' in session:
        base_bytes = bytes(session['last_generated_image'])

    # Regenera imagem
    chat = await image_generation_service.get_or_create_chat(user_number)
    generation_result = (
        await image_generation_service.generate_content_from_chat(
            last_prompt, chat, [base_bytes] if base_bytes else None
        )
    )

    if not generation_result:
        await whatsapp_service.send_message(
            sender,
            "Falha ao regenerar. Ajuste o prompt com 'imagem <novo prompt>'",
        )
        return

    generated_bytes = generation_result[0]

    # Envia e atualiza
    await whatsapp_service.send_image_message(
        sender, generated_bytes, f'Variação gerada: {last_prompt}'
    )
    await _delete_latest_status(whatsapp_service)

    # Gera legenda para variação
    contact_info = await whatsapp_service.get_contact_info(user_number)
    user_name = contact_info.get('name') if contact_info else None

    status_caption = await _generate_status_caption(
        image_generation_service, f'Variação: {last_prompt}', user_name, chat
    )
    status_id = await whatsapp_service.post_status_update(
        generated_bytes, status_caption
    )

    # Atualiza dados
    await collection.update_one(
        {'user_number': user_number},
        {
            '$set': {
                'last_generated_image': generated_bytes,
                'last_status_id': status_id,
            }
        },
    )
    await _update_status_cache(db, generated_bytes, last_prompt, status_id)

    await whatsapp_service.send_message(sender, '✅ Variação pronta.')
    logger.success(f'🔁 Refazer concluído user={user_number}')


async def _handle_editar_command(
    command_data: dict,
    image_generation_service: Any,
    whatsapp_service: WhatsAppService,
    db: AsyncIOMotorDatabase,
):
    """Handler para comando 'editar'."""
    argument = command_data.get('argument', '')
    sender = command_data.get('sender')
    user_number = command_data.get('user_number')
    original_payload = command_data.get('original_payload', {})

    if not argument:
        await whatsapp_service.send_message(
            sender,
            'Uso: editar <instruções>. Ex: editar adicionar brilho roxo',
        )
        return

    # Coleta imagens para edição
    collection = db.get_collection('user_sessions')
    session = await collection.find_one({'user_number': user_number})

    images_for_editing = []

    # Adiciona imagem da sessão
    if session and 'last_generated_image' in session:
        images_for_editing.append(bytes(session['last_generated_image']))

    # Adiciona novas imagens do payload
    media_paths = _extract_media_paths(original_payload)
    new_images = await _download_media_files(whatsapp_service, media_paths)
    images_for_editing.extend(new_images)

    if not images_for_editing:
        await whatsapp_service.send_message(
            sender,
            'Nenhuma imagem encontrada para editar. '
            'Envie uma imagem ou use o comando `imagem` primeiro.',
        )
        return

    # Gera edição
    combined_prompt = f'Edite esta imagem: {argument}'
    chat = await image_generation_service.get_or_create_chat(user_number)
    generation_result = (
        await image_generation_service.generate_content_from_chat(
            combined_prompt, chat, images_for_editing
        )
    )

    if not generation_result:
        await whatsapp_service.send_message(
            sender, "Falha ao editar. Refine as instruções ou tente 'refazer'."
        )
        return

    # Processa resultados
    for i, edited_bytes in enumerate(generation_result):
        caption = (
            f'Edição: {argument}'
            if len(generation_result) == 1
            else f'Edição: {argument} ({i + 1}/{len(generation_result)})'
        )
        await whatsapp_service.send_image_message(
            sender, edited_bytes, caption
        )

        # Apenas a primeira imagem atualiza status e sessão
        if i == 0:
            await _delete_latest_status(whatsapp_service)

            # Gera legenda para edição
            contact_info = await whatsapp_service.get_contact_info(user_number)
            user_name = contact_info.get('name') if contact_info else None

            temp_chat = await image_generation_service.get_or_create_chat(
                f'edit_caption_{user_number}'
            )
            status_caption = await _generate_status_caption(
                image_generation_service,
                f'Edição: {argument}',
                user_name,
                temp_chat,
            )

            status_id = await whatsapp_service.post_status_update(
                edited_bytes, status_caption
            )

            # Atualiza dados
            await collection.update_one(
                {'user_number': user_number},
                {
                    '$set': {
                        'last_generated_image': edited_bytes,
                        'last_prompt': combined_prompt,
                        'last_status_id': status_id,
                    }
                },
            )
            await _update_status_cache(
                db, edited_bytes, combined_prompt, status_id
            )

    await whatsapp_service.send_message(sender, '✅ Edição concluída.')
    logger.success(f'✏️ Edição concluída user={user_number}')


async def process_command_operation(
    command_data: dict,
    image_generation_service: Any,
    whatsapp_service: WhatsAppService,
    db: AsyncIOMotorDatabase,
):
    """Processa comandos em background."""
    operation = command_data.get('operation')
    sender = command_data.get('sender')
    user_number = command_data.get('user_number')

    logger.info(f'⚙️ Processando comando {operation} user={user_number}')

    try:
        handlers = {
            'imagem': _handle_imagem_command,
            'legenda': _handle_legenda_command,
            'refazer': _handle_refazer_command,
            'editar': _handle_editar_command,
        }

        handler = handlers.get(operation)
        if handler:
            if operation == 'legenda':
                await handler(command_data, whatsapp_service, db)
            else:
                await handler(
                    command_data,
                    image_generation_service,
                    whatsapp_service,
                    db,
                )
        else:
            logger.warning(f'⚠️ Operação desconhecida: {operation}')

    except Exception as e:
        logger.error(
            f'❌ Erro ao processar comando {operation} user={user_number}: {e}'
        )
        logger.exception('Detalhes do erro:')
        try:
            await whatsapp_service.send_message(
                sender, 'Erro interno no processamento do comando.'
            )
        except Exception:
            pass


def _handle_status_view(
    data: dict, background_tasks: BackgroundTasks, deps: WebhookDependencies
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
        return {'status': 'ignored', 'detail': 'command_without_sender'}

    # AJUDA: responde imediatamente
    if cmd_ctx.operation == CommandOperation.AJUDA:
        await deps.whatsapp_service.send_message(sender, HELP_MESSAGE)
        return {
            'status': 'accepted',
            'detail': 'help_sent',
            'command': 'ajuda',
        }

    # Mapeia operação
    operation_map = {
        CommandOperation.IMAGEM: 'imagem',
        CommandOperation.LEGENDA: 'legenda',
        CommandOperation.REFAZER: 'refazer',
        CommandOperation.EDITAR: 'editar',
    }
    operation_str = operation_map.get(cmd_ctx.operation)

    # Feedback imediato
    await deps.whatsapp_service.send_message(
        sender, f'⚙️ Processando comando {operation_str}...'
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
    """Recebe webhooks do go-whatsapp e processa comandos/eventos."""
    try:
        data = await request.json()
        user_number = extract_primary_user_number(data)
        contact_info = await deps.whatsapp_service.get_contact_info(
            user_number
        )

        logger.bind(payload=data).info(
            f'Contato: {contact_info} recebeu sua mensagem'
        )

        # Fluxo 1: Visualização de status
        status_result = _handle_status_view(data, background_tasks, deps)
        if status_result:
            return status_result

        # Fluxo 2: Comandos
        message_body = data.get('message', {})
        image_body = data.get('image', {})
        message_text = (
            message_body.get('text')
            or message_body.get('caption')
            or image_body.get('caption')
        )

        cmd_ctx = parse_command(message_text)
        if cmd_ctx:
            command_result = await _handle_command(
                data, cmd_ctx, background_tasks, deps
            )
            if command_result:
                return command_result

        # Nenhum comando ou evento detectado
        logger.debug(
            'Nenhum comando ou evento de status detectado. Ignorando.'
        )
        return {'status': 'ok', 'reason': 'no_command_or_event'}

    except Exception as e:
        logger.error(f'❌ Erro no webhook: {e}')
        logger.exception('Detalhes do erro:')
        return {'status': 'error', 'detail': str(e)}
    finally:
        logger.debug('🔌 Webhook principal finalizado')
