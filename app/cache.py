from datetime import datetime, timedelta
from typing import Any, Optional

from bson import Binary
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import IndexModel

from .database import get_cache_collection
from .logger import logger


class MongoCache:
    """
    Sistema de cache unificado usando apenas MongoDB.
    Substitui completamente o cache em memória e híbrido anterior.
    """

    def __init__(self, collection: AsyncIOMotorCollection):
        self._collection = collection

    async def _ensure_indexes(self):
        """Garante que os índices necessários existam para performance."""
        try:
            indexes = [
                IndexModel([('cache_key', 1)], unique=True),
                IndexModel([('expires_at', 1)], expireAfterSeconds=0),
                IndexModel([('cache_type', 1)]),
                IndexModel([('created_at', 1)]),
            ]
            await self._collection.create_indexes(indexes)
            logger.debug('📊 Índices do cache MongoDB criados/verificados')
        except Exception as e:
            logger.warning(f'⚠️ Erro ao criar índices do cache: {e}')

    async def set(
        self,
        key: str,
        value: Any,
        cache_type: str = 'general',
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        """
        Armazena um valor no cache com TTL opcional.

        Args:
            key: Chave única para o cache
            value: Valor a ser armazenado (será serializado)
            cache_type: Tipo do cache para organização
            ttl_seconds: Tempo de vida em segundos (None = sem expiração)
        """
        try:
            await self._ensure_indexes()

            doc = {
                'cache_key': key,
                'cache_type': cache_type,
                'value': value,
                'created_at': datetime.utcnow(),
            }

            if ttl_seconds:
                doc['expires_at'] = datetime.utcnow() + timedelta(
                    seconds=ttl_seconds
                )

            await self._collection.replace_one(
                {'cache_key': key}, doc, upsert=True
            )

            logger.debug(f'💾 Cache salvo: {key} ({cache_type})')
            return True
        except Exception as e:
            logger.error(f'❌ Erro ao salvar cache {key}: {e}')
            return False

    async def get(self, key: str) -> Any:
        """
        Recupera um valor do cache.

        Args:
            key: Chave do cache

        Returns:
            Valor armazenado ou None se não encontrado/expirado
        """
        try:
            doc = await self._collection.find_one({'cache_key': key})

            if not doc:
                return None

            # Verifica expiração manual (backup do TTL automático do MongoDB)
            if 'expires_at' in doc and doc['expires_at'] < datetime.utcnow():
                await self.delete(key)
                return None

            logger.debug(f'📖 Cache recuperado: {key}')
            return doc.get('value')
        except Exception as e:
            logger.error(f'❌ Erro ao ler cache {key}: {e}')
            return None

    async def delete(self, key: str) -> bool:
        """Remove um item do cache."""
        try:
            result = await self._collection.delete_one({'cache_key': key})
            if result.deleted_count > 0:
                logger.debug(f'🗑️ Cache removido: {key}')
                return True
            return False
        except Exception as e:
            logger.error(f'❌ Erro ao deletar cache {key}: {e}')
            return False

    async def exists(self, key: str) -> bool:
        """Verifica se uma chave existe no cache."""
        try:
            doc = await self._collection.find_one(
                {'cache_key': key}, {'_id': 1}
            )
            return doc is not None
        except Exception as e:
            logger.error(
                f'❌ Erro ao verificar existência do cache {key}: {e}'
            )
            return False

    async def clear_by_type(self, cache_type: str) -> int:
        """Remove todos os itens de um tipo específico."""
        try:
            result = await self._collection.delete_many({
                'cache_type': cache_type
            })
            logger.info(
                f'🗑️ {result.deleted_count} '
                f"itens do cache tipo '{cache_type}' removidos"
            )
            return result.deleted_count
        except Exception as e:
            logger.error(f'❌ Erro ao limpar cache tipo {cache_type}: {e}')
            return 0

    async def clear_expired(self) -> int:
        """Remove manualmente itens expirados (backup do TTL automático)."""
        try:
            result = await self._collection.delete_many({
                'expires_at': {'$lt': datetime.utcnow()}
            })
            if result.deleted_count > 0:
                logger.info(
                    f'🗑️ {result.deleted_count}'
                    ' itens expirados removidos do cache'
                )
            return result.deleted_count
        except Exception as e:
            logger.error(f'❌ Erro ao limpar cache expirado: {e}')
            return 0

    async def get_stats(self) -> dict:
        """Retorna estatísticas do cache."""
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': '$cache_type',
                        'count': {'$sum': 1},
                        'total_size': {'$sum': {'$bsonSize': '$$ROOT'}},
                    }
                }
            ]

            stats = {}
            async for result in self._collection.aggregate(pipeline):
                stats[result['_id']] = {
                    'count': result['count'],
                    'size_bytes': result['total_size'],
                }

            # Total geral
            total_docs = await self._collection.count_documents({})
            stats['_total'] = {'count': total_docs}

            return stats
        except Exception as e:
            logger.error(f'❌ Erro ao obter estatísticas do cache: {e}')
            return {}


class StatusImageCache:
    """
    Cache especializado para imagens de status do WhatsApp.
    Agora usa apenas MongoDB através do MongoCache.
    """

    def __init__(self, mongo_cache: MongoCache):
        self._cache = mongo_cache
        self._status_image_key = 'whatsapp:last_status_image'
        self._status_id_key = 'whatsapp:last_status_id'

    async def save_status_image(self, image_bytes: bytes) -> bool:
        """Salva a imagem de status mais recente no MongoDB."""
        try:
            # Converte bytes para Binary do MongoDB
            binary_data = Binary(image_bytes)
            success = await self._cache.set(
                self._status_image_key, binary_data, cache_type='status_image'
            )

            if success:
                logger.info('📁 Imagem de status salva no cache MongoDB.')
            return success
        except Exception as e:
            logger.error(f'❌ Erro ao salvar imagem de status: {e}')
            return False

    async def get_last_status_image(self) -> Optional[bytes]:
        """Recupera a última imagem de status do MongoDB."""
        try:
            binary_data = await self._cache.get(self._status_image_key)
            if binary_data:
                return bytes(binary_data)

            logger.warning('🖼️ Nenhuma imagem de status encontrada no cache.')
            return None
        except Exception as e:
            logger.error(f'❌ Erro ao ler imagem de status: {e}')
            return None

    async def save_last_status_id(self, status_id: str) -> bool:
        """Salva o ID do último status postado no MongoDB."""
        try:
            success = await self._cache.set(
                self._status_id_key, status_id, cache_type='status_id'
            )

            if success:
                logger.info(f'🆔 ID do status salvo no cache: {status_id}')
            return success
        except Exception as e:
            logger.error(f'❌ Erro ao salvar ID do status: {e}')
            return False

    async def get_last_status_id(self) -> Optional[str]:
        """Recupera o ID do último status postado do MongoDB."""
        try:
            status_id = await self._cache.get(self._status_id_key)
            return status_id
        except Exception as e:
            logger.error(f'❌ Erro ao ler ID do status: {e}')
            return None

    async def clear_status_cache(self) -> bool:
        """Limpa o cache de status (imagem e ID)."""
        try:
            image_deleted = await self._cache.delete(self._status_image_key)
            id_deleted = await self._cache.delete(self._status_id_key)

            if image_deleted or id_deleted:
                logger.info('🗑️ Cache de status limpo.')
                return True
            return False
        except Exception as e:
            logger.error(f'❌ Erro ao limpar cache de status: {e}')
            return False


class MessageCache:
    """
    Cache para evitar processamento duplicado de mensagens.
    Substitui o cache em memória anterior.
    """

    def __init__(self, mongo_cache: MongoCache):
        self._cache = mongo_cache
        self._default_ttl = 300  # 5 minutos

    async def is_message_processed(self, message_id: str) -> bool:
        """
        Verifica se a mensagem já foi processada e a marca como processada.

        Args:
            message_id: ID único da mensagem

        Returns:
            True se já foi processada, False caso contrário
        """
        try:
            cache_key = f'message:processed:{message_id}'

            # Verifica se já existe
            if await self._cache.exists(cache_key):
                logger.debug(f'🔄 Mensagem duplicata detectada: {message_id}')
                return True

            # Marca como processada com TTL
            await self._cache.set(
                cache_key,
                {
                    'processed_at': datetime.utcnow().isoformat(),
                    'message_id': message_id,
                },
                cache_type='message_processing',
                ttl_seconds=self._default_ttl,
            )

            logger.debug(f'✅ Mensagem marcada como processada: {message_id}')
            return False
        except Exception as e:
            logger.error(
                f'❌ Erro ao verificar mensagem processada {message_id}: {e}'
            )
            return False

    async def cleanup_processed_messages(self) -> int:
        """Remove mensagens processadas expiradas."""
        return await self._cache.clear_expired()


# Factory functions para dependency injection
async def get_mongo_cache() -> MongoCache:
    """Factory para MongoCache."""
    return MongoCache(get_cache_collection())


async def get_status_image_cache() -> StatusImageCache:
    """Factory para StatusImageCache."""
    mongo_cache = await get_mongo_cache()
    return StatusImageCache(mongo_cache)


async def get_message_cache() -> MessageCache:
    """Factory para MessageCache."""
    mongo_cache = await get_mongo_cache()
    return MessageCache(mongo_cache)
