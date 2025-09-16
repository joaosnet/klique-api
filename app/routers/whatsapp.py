from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from langchain_core.messages import HumanMessage
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase

from app.agents.orquestrador import create_graph_runnable

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
) -> bool:
    """Verifica se uma mensagem já foi processada anteriormente."""
    try:
        collection = db.get_collection('processed_messages')
        existing_message = await collection.find_one({
            'message_id': message_id,
            'user_number': user_number,
        })

        if existing_message:
            logger.info(
                f'📋 Mensagem {message_id} já processada para {user_number}'
            )
            return True
        return False
    except Exception as e:
        logger.error(f'❌ Erro ao verificar mensagem processada: {e}')
        # Em caso de erro, permite o processamento para evitar bloqueios
        return False


async def _mark_message_as_processed(
    db: AsyncIOMotorDatabase,
    message_id: str,
    user_number: str,
    message_text: str,
) -> None:
    """Marca uma mensagem como processada no cache."""
    try:
        collection = db.get_collection('processed_messages')
        await collection.insert_one({
            'message_id': message_id,
            'user_number': user_number,
            'message_text': message_text,
            'processed_at': datetime.utcnow(),
        })
        logger.info(f'✅ Mensagem {message_id} marcada como processada')
    except Exception as e:
        logger.error(f'❌ Erro ao marcar mensagem como processada: {e}')


async def _cleanup_old_processed_messages(db: AsyncIOMotorDatabase) -> None:
    """Remove mensagens processadas com mais de 24 horas."""
    try:
        collection = db.get_collection('processed_messages')
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)

        result = await collection.delete_many({
            'processed_at': {'$lt': twenty_four_hours_ago}
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

        # Fluxo 2: Orquestrador (restrito ao número do João Neto)
        message_body = data.get('message', {})
        image_body = data.get('image', {})
        message_text = (
            message_body.get('text')
            or message_body.get('caption')
            or image_body.get('caption')
        )
        if message_text:
            # Permite apenas o número do João Neto conversar com a IA
            if user_number != '559184497318':
                logger.info(
                    f'🔒 Usuário {user_number} bloqueado para chat com IA.'
                )
                # await deps.whatsapp_service.send_message(
                #     user_number,
                #     (
                #         '🚫 Apenas o administrador pode conversar com a IA '
                #         'no momento.'
                #     ),
                # )
                return {'status': 'ok', 'detail': 'restricted_access'}
            # Verifica se a mensagem possui ID e se já foi processada
            message_id = message_body.get('id')
            if message_id:
                logger.info(
                    f'🔍 Verificando duplicata para mensagem ID: {message_id}'
                )
                # Verifica se mensagem já foi processada
                already_processed = await _is_message_already_processed(
                    deps.db, message_id, user_number
                )
                if already_processed:
                    logger.warning(
                        f'🔄 Mensagem duplicada ignorada: {message_id} '
                        f'do usuário {user_number}'
                    )
                    return {
                        'status': 'ok',
                        'detail': 'duplicate_message_ignored',
                    }
                logger.info(f'✅ Mensagem {message_id} é nova, processando...')
                # Marca mensagem como processada ANTES do processamento
                # para evitar duplicatas durante o processamento
                await _mark_message_as_processed(
                    deps.db, message_id, user_number, message_text
                )
                # Adiciona tarefa de limpeza em background
                # (executa esporadicamente)
                background_tasks.add_task(
                    _cleanup_old_processed_messages, deps.db
                )
            else:
                logger.warning(
                    '⚠️ Mensagem sem ID, não é possível verificar duplicatas'
                )
            logger.info(
                f'🤖 Mensagem recebida para o orquestrador: "{message_text}"'
            )
            graph = create_graph_runnable()
            resposta = await graph.ainvoke({
                'messages': [HumanMessage(content=message_text)],
                'next': None,
            })
            final_response = resposta['messages'][-1].content
            # Se o agente de marketing retornou imagem, envie como mídia
            image_bytes = None
            # Tenta extrair imagem do retorno (caso seja dict)
            if isinstance(final_response, dict):
                image_bytes = final_response.get('image_bytes')
                message_text_to_send = final_response.get('message', '')
            else:
                message_text_to_send = final_response

            if image_bytes:
                # Envia imagem como mídia via WhatsApp
                try:
                    message_id = await deps.whatsapp_service._send_image(
                        user_number,
                        image_bytes,
                        message_text_to_send,
                        filename='imagem_gerada.png',
                    )
                    logger.info(f'🖼️ Imagem enviada com ID: {message_id}')
                except Exception as e:
                    logger.error(f'❌ Erro ao enviar imagem gerada: {e}')
            else:
                # Envia apenas texto se não houver imagem
                await deps.whatsapp_service.send_message(
                    user_number, message_text_to_send
                )
            return {'status': 'ok', 'detail': 'processed_by_orchestrator'}

        # Nenhum comando ou evento detectado
        logger.debug(
            'Nenhuma mensagem de texto ou evento de status detectado.'
            ' Ignorando.'
        )
        return {'status': 'ok', 'reason': 'no_text_or_event'}

    except Exception as e:
        logger.error(f'❌ Erro no webhook: {e}')
        logger.exception('Detalhes do erro:')
        return {'status': 'error', 'detail': str(e)}
    finally:
        logger.debug('🔌 Webhook principal finalizado')
