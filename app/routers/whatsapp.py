from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.agents.tasks import process_message_with_agent

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
    base_images_bytes: Optional[list[bytes]] = None
    status_id: Optional[str] = None


router = APIRouter(prefix='/webhooks', tags=['webhooks'])

NO_SESSION_FALLBACK = (
    'Nenhuma imagem anterior encontrada. Envie: imagem <prompt>'
)


async def _is_message_already_processed(
    db: AsyncIOMotorDatabase, message_id: str, user_number: str
) -> tuple[bool, bool]:
    """Verifica se uma mensagem já foi processada anteriormente.

    Returns:
        tuple: (já_processada, deve_tentar_novamente)
    """
    try:
        collection = db.get_collection('processed_messages')
        existing_message = await collection.find_one({
            'message_id': message_id,
            'user_number': user_number,
        })

        already_processed = False
        should_retry = True

        if not existing_message:
            return already_processed, should_retry

        status = existing_message.get('status', 'completed')
        attempts = existing_message.get('attempts', 0)
        last_attempt = existing_message.get('last_attempt')
        max_attempts = 3  # Máximo de tentativas
        now = datetime.utcnow()
        five_minutes_ago = now - timedelta(minutes=5)

        if status == 'completed':
            logger.info(
                f'📋 Mensagem {message_id} já processada '
                f'com sucesso para {user_number}'
            )
            already_processed = True
            should_retry = False
        elif status == 'failed':
            logger.info(
                f'📋 Mensagem {message_id} falhou anteriormente '
                f'para {user_number}'
            )
            already_processed = True
            should_retry = False
        elif status == 'processing':
            if last_attempt and last_attempt > five_minutes_ago:
                logger.info(
                    f'📋 Mensagem {message_id} ainda em processamento '
                    f'para {user_number}'
                )
                already_processed = True
                should_retry = False
            elif attempts >= max_attempts:
                # Marca como falhou
                await collection.update_one(
                    {'message_id': message_id, 'user_number': user_number},
                    {'$set': {'status': 'failed', 'last_attempt': now}},
                )
                logger.warning(
                    f'📋 Mensagem {message_id} excedeu limite '
                    f'de tentativas para {user_number}'
                )
                already_processed = True
                should_retry = False
            else:
                # Pode tentar novamente
                logger.info(
                    f'📋 Mensagem {message_id} será retentada '
                    f'para {user_number} (tentativa {attempts + 1})'
                )
                already_processed = False
                should_retry = True
        else:
            # Default: tentar
            already_processed = False
            should_retry = True

        return already_processed, should_retry

    except Exception as e:
        logger.error(f'❌ Erro ao verificar mensagem processada: {e}')
        return False, True


@dataclass
class MessageProcessingData:
    """Dados para marcar mensagem como processada."""
    message_id: str
    user_number: str
    message_text: str
    status: str = 'completed'
    attempts: int = 0


async def _mark_message_as_processed(
    db: AsyncIOMotorDatabase, data: MessageProcessingData
) -> None:
    """Marca uma mensagem como processada no cache."""
    try:
        collection = db.get_collection('processed_messages')
        now = datetime.utcnow()

        # Tenta atualizar se já existe, senão insere
        result = await collection.update_one(
            {'message_id': data.message_id, 'user_number': data.user_number},
            {
                '$set': {
                    'message_text': data.message_text,
                    'status': data.status,
                    'attempts': data.attempts,
                    'last_attempt': now,
                    'processed_at': now,
                },
                '$setOnInsert': {
                    'message_id': data.message_id,
                    'user_number': data.user_number,
                },
            },
            upsert=True,
        )

        if result.upserted_id:
            logger.info(
                f'✅ Mensagem {data.message_id} inserida como {data.status}'
            )
        else:
            logger.info(
                f'✅ Mensagem {data.message_id} atualizada para {data.status}'
            )

    except Exception as e:
        logger.error(f'❌ Erro ao marcar mensagem como processada: {e}')


async def _cleanup_old_processed_messages(db: AsyncIOMotorDatabase) -> None:
    """Remove mensagens processadas com mais de 24 horas."""
    try:
        collection = db.get_collection('processed_messages')
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)

        result = await collection.delete_many({
            '$or': [
                {'processed_at': {'$lt': twenty_four_hours_ago}},
                {'last_attempt': {'$lt': twenty_four_hours_ago}},
            ]
        })

        if result.deleted_count > 0:
            logger.debug(
                f'🧹 Removidas {result.deleted_count} '
                'mensagens antigas do cache'
            )
    except Exception as e:
        logger.error(f'❌ Erro ao limpar mensagens antigas: {e}')


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
    user_name: Optional[str] = None,
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
        if not user_number:
            logger.warning('⚠️ User number not found in status view, skipping.')
            return

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
        if not user_number:
            logger.warning('⚠️ User number not found in status view, skipping.')
            return
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


async def _delete_latest_status(whatsapp_service: WhatsAppService) -> bool:
    """Deleta o status mais recente.

    :return: True se deletou com sucesso ou não havia status, False se houve erro crítico.
    """  # noqa: E501
    try:
        latest_status_id = await whatsapp_service.get_latest_status_id()
        if latest_status_id:
            logger.info(f'🗑️ Deletando status: {latest_status_id}')
            deletion_success = await whatsapp_service.delete_status(
                latest_status_id
            )
            if deletion_success:
                logger.success(
                    f'✅ Status {latest_status_id} deletado com sucesso'
                )
                return True
            else:
                logger.warning(f'⚠️ Falha ao deletar status {latest_status_id}')
                return False
        else:
            logger.info('📋 Nenhum status encontrado para deletar')
            return True
    except Exception as e:
        logger.warning(f'⚠️ Erro inesperado ao deletar status: {e}')
        # Não interrompe o fluxo principal por erro de deleção
        return False


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


async def _update_status_cache(
    db: AsyncIOMotorDatabase,
    image_bytes: bytes,
    prompt: str,
    status_id: str | None = None,
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


def _validate_message_access(data: dict, user_number: str) -> dict | None:
    """Valida acesso à mensagem e retorna resposta de erro se inválido."""
    # Permite apenas o número do João Neto conversar com a IA
    if user_number != '559184497318':
        logger.info(
            f'🔒 Usuário {user_number} bloqueado para chat com IA.'
        )
        return {'status': 'ok', 'detail': 'restricted_access'}

    # Permite apenas mensagens no chat consigo mesmo
    chat_id = data.get('chat_id')
    if chat_id != '559184497318':
        logger.info(
            f'🔒 Mensagem não é do chat consigo mesmo '
            f'(chat_id: {chat_id}).'
        )
        return {'status': 'ok', 'detail': 'not_self_chat'}

    return None  # Acesso válido


async def _process_message_request(
    data: dict, user_number: str, deps: WebhookDependencies
) -> dict:
    """Processa uma solicitação de mensagem."""
    # Extrai dados da mensagem
    message_body = data.get('message', {})
    image_body = data.get('image', {})
    message_text = (
        message_body.get('text')
        or message_body.get('caption')
        or image_body.get('caption')
    )
    message_id = message_body.get('id') or image_body.get('id')

    if not message_text:
        return {'status': 'ok', 'reason': 'no_text_or_event'}

    # Validações de acesso
    access_error = _validate_message_access(data, user_number)
    if access_error:
        return access_error

    # Limpa mensagens processadas antigas
    await _cleanup_old_processed_messages(deps.db)

    # Verifica se a mensagem já foi processada
    if message_id:
        (
            already_processed,
            should_retry,
        ) = await _is_message_already_processed(
            deps.db, message_id, user_number
        )
        if already_processed:
            logger.info(f'Mensagem duplicada recusada: {message_id}')
            return {
                'status': 'duplicate',
                'detail': 'Mensagem já processada',
            }

    # Marca como em processamento
    if message_id:
        await _mark_message_as_processed(
            deps.db,
            MessageProcessingData(
                message_id=message_id,
                user_number=user_number,
                message_text=message_text,
                status='processing',
                attempts=0,
            ),
        )

    # Processa a mensagem normalmente
    try:
        response = await process_message_with_agent(
            user_number=user_number,
            message_text=message_text,
            whatsapp_service=deps.whatsapp_service,
        )

        # Marca como processada após sucesso
        if message_id:
            await _mark_message_as_processed(
                deps.db,
                MessageProcessingData(
                    message_id=message_id,
                    user_number=user_number,
                    message_text=message_text,
                    status='completed',
                    attempts=0,
                ),
            )
        return response

    except Exception:
        # Em caso de erro, marca como falhou e incrementa tentativas
        if message_id:
            # Busca tentativas atuais
            collection = deps.db.get_collection('processed_messages')
            existing = await collection.find_one({
                'message_id': message_id,
                'user_number': user_number,
            })
            current_attempts = (
                existing.get('attempts', 0) if existing else 0
            )

            await _mark_message_as_processed(
                deps.db,
                MessageProcessingData(
                    message_id=message_id,
                    user_number=user_number,
                    message_text=message_text,
                    status='failed',
                    attempts=current_attempts + 1,
                ),
            )
        raise  # Re-raise para o tratamento de erro geral


@router.post('/whatsapp')
async def receive_whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    deps: WebhookDependencies = Depends(get_webhook_dependencies),
):
    """Recebe webhooks do go-whatsapp e processa comandos/eventos."""
    try:
        data = await request.json()
        logger.bind(payload=data).info(f'📩 Webhook recebido: {data}')
        user_number = extract_primary_user_number(data)
        if not user_number:
            logger.warning('⚠️ User number not found, ignoring.')
            return {'status': 'ignored', 'reason': 'no_user_number'}

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

        # Fluxo 2: Processamento de mensagem
        return await _process_message_request(data, user_number, deps)

    except Exception as e:
        logger.error(f'❌ Erro no webhook: {e}')
        logger.exception('Detalhes do erro:')
        return {'status': 'error', 'detail': str(e)}
    finally:
        logger.debug('🔌 Webhook principal finalizado')
