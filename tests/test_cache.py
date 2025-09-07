from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from app.cache import MessageCache, MongoCache, StatusImageCache

# Constantes para evitar magic numbers
EXPECTED_DELETED_COUNT = 5
EXPECTED_DELETE_CALLS = 2
DEFAULT_TTL_SECONDS = 300  # 5 minutos


@pytest.fixture
async def mock_collection():
    """Mock da collection do MongoDB."""
    collection = AsyncMock()
    collection.create_indexes = AsyncMock()
    collection.replace_one = AsyncMock()
    collection.find_one = AsyncMock()
    collection.delete_one = AsyncMock()
    collection.delete_many = AsyncMock()
    collection.count_documents = AsyncMock()
    collection.aggregate = AsyncMock()
    return collection


@pytest.fixture
async def mongo_cache(mock_collection):
    """Instância do MongoCache com collection mockada."""
    return MongoCache(mock_collection)


async def test_set_value_success(mongo_cache, mock_collection):
    """Testa se valores são armazenados corretamente."""
    mock_collection.replace_one.return_value.acknowledged = True

    result = await mongo_cache.set('test_key', 'test_value', 'test_type')

    assert result is True
    mock_collection.replace_one.assert_called_once()


async def test_get_value_success(mongo_cache, mock_collection):
    """Testa se valores são recuperados corretamente."""
    expected_doc = {
        'cache_key': 'test_key',
        'value': 'test_value',
        'created_at': datetime.utcnow(),
    }
    mock_collection.find_one.return_value = expected_doc

    result = await mongo_cache.get('test_key')

    assert result == 'test_value'
    mock_collection.find_one.assert_called_once_with({'cache_key': 'test_key'})


async def test_get_value_not_found(mongo_cache, mock_collection):
    """Testa comportamento quando valor não é encontrado."""
    mock_collection.find_one.return_value = None

    result = await mongo_cache.get('nonexistent_key')

    assert result is None


async def test_get_value_expired(mongo_cache, mock_collection):
    """Testa se valores expirados são removidos."""
    expired_doc = {
        'cache_key': 'expired_key',
        'value': 'expired_value',
        'expires_at': datetime.utcnow() - timedelta(hours=1),
    }
    mock_collection.find_one.return_value = expired_doc
    mock_collection.delete_one.return_value.deleted_count = 1

    result = await mongo_cache.get('expired_key')

    assert result is None
    mock_collection.delete_one.assert_called_once()


async def test_delete_value(mongo_cache, mock_collection):
    """Testa remoção de valores."""
    mock_collection.delete_one.return_value.deleted_count = 1

    result = await mongo_cache.delete('test_key')

    assert result is True
    mock_collection.delete_one.assert_called_once_with({
        'cache_key': 'test_key'
    })


async def test_exists_true(mongo_cache, mock_collection):
    """Testa verificação de existência quando a chave existe."""
    mock_collection.find_one.return_value = {'_id': 'some_id'}

    result = await mongo_cache.exists('test_key')

    assert result is True


async def test_exists_false(mongo_cache, mock_collection):
    """Testa verificação de existência quando a chave não existe."""
    mock_collection.find_one.return_value = None

    result = await mongo_cache.exists('test_key')

    assert result is False


async def test_clear_by_type(mongo_cache, mock_collection):
    """Testa limpeza por tipo de cache."""
    mock_collection.delete_many.return_value.deleted_count = (
        EXPECTED_DELETED_COUNT
    )

    result = await mongo_cache.clear_by_type('test_type')

    assert result == EXPECTED_DELETED_COUNT
    mock_collection.delete_many.assert_called_once_with({
        'cache_type': 'test_type'
    })


async def test_set_with_ttl(mongo_cache, mock_collection):
    """Testa armazenamento com TTL."""
    mock_collection.replace_one.return_value.acknowledged = True

    result = await mongo_cache.set(
        'test_key', 'test_value', ttl_seconds=DEFAULT_TTL_SECONDS
    )

    assert result is True
    # Verifica se o documento foi criado com expires_at
    call_args = mock_collection.replace_one.call_args[0][1]
    assert 'expires_at' in call_args


@pytest.fixture
async def mock_mongo_cache():
    """Mock do MongoCache."""
    mock_cache = AsyncMock()
    mock_cache.set = AsyncMock(return_value=True)
    mock_cache.get = AsyncMock()
    mock_cache.delete = AsyncMock(return_value=True)
    return mock_cache


@pytest.fixture
async def status_cache(mock_mongo_cache):
    """Instância do StatusImageCache com MongoCache mockado."""
    return StatusImageCache(mock_mongo_cache)


async def test_save_status_image(status_cache, mock_mongo_cache):
    """Testa salvamento de imagem de status."""
    test_image_bytes = b'fake_image_data'

    result = await status_cache.save_status_image(test_image_bytes)

    assert result is True
    mock_mongo_cache.set.assert_called_once()
    call_args, call_kwargs = mock_mongo_cache.set.call_args
    assert call_args[0] == 'whatsapp:last_status_image'
    assert call_kwargs.get('cache_type') == 'status_image'


async def test_get_last_status_image(status_cache, mock_mongo_cache):
    """Testa recuperação de imagem de status."""
    test_image_bytes = b'fake_image_data'
    mock_mongo_cache.get.return_value = test_image_bytes

    result = await status_cache.get_last_status_image()

    assert result == test_image_bytes
    mock_mongo_cache.get.assert_called_once_with('whatsapp:last_status_image')


async def test_get_last_status_image_none(status_cache, mock_mongo_cache):
    """Testa recuperação quando não há imagem."""
    mock_mongo_cache.get.return_value = None

    result = await status_cache.get_last_status_image()

    assert result is None


async def test_save_last_status_id(status_cache, mock_mongo_cache):
    """Testa salvamento de ID de status."""
    test_status_id = 'status_123'

    result = await status_cache.save_last_status_id(test_status_id)

    assert result is True
    mock_mongo_cache.set.assert_called_once()
    call_args, call_kwargs = mock_mongo_cache.set.call_args
    assert call_args[0] == 'whatsapp:last_status_id'
    assert call_args[1] == test_status_id
    assert call_kwargs.get('cache_type') == 'status_id'


async def test_get_last_status_id(status_cache, mock_mongo_cache):
    """Testa recuperação de ID de status."""
    test_status_id = 'status_123'
    mock_mongo_cache.get.return_value = test_status_id

    result = await status_cache.get_last_status_id()

    assert result == test_status_id
    mock_mongo_cache.get.assert_called_once_with('whatsapp:last_status_id')


async def test_clear_status_cache(status_cache, mock_mongo_cache):
    """Testa limpeza do cache de status."""
    result = await status_cache.clear_status_cache()

    assert result is True
    assert mock_mongo_cache.delete.call_count == EXPECTED_DELETE_CALLS


@pytest.fixture
async def mock_message_cache():
    """Mock do MongoCache para MessageCache."""
    mock_cache = AsyncMock()
    mock_cache.exists = AsyncMock()
    mock_cache.set = AsyncMock(return_value=True)
    mock_cache.clear_expired = AsyncMock(return_value=0)
    return mock_cache


@pytest.fixture
async def message_cache(mock_message_cache):
    """Instância do MessageCache com MongoCache mockado."""
    return MessageCache(mock_message_cache)


async def test_is_message_processed_new(message_cache, mock_message_cache):
    """Testa processamento de nova mensagem."""
    mock_message_cache.exists.return_value = False

    result = await message_cache.is_message_processed('msg_123')

    assert result is False
    mock_message_cache.exists.assert_called_once()
    mock_message_cache.set.assert_called_once()


async def test_is_message_processed_duplicate(
    message_cache, mock_message_cache
):
    """Testa detecção de mensagem duplicada."""
    mock_message_cache.exists.return_value = True

    result = await message_cache.is_message_processed('msg_123')

    assert result is True
    mock_message_cache.exists.assert_called_once()
    # set não deve ser chamado para mensagens duplicadas
    mock_message_cache.set.assert_not_called()


async def test_cleanup_processed_messages(message_cache, mock_message_cache):
    """Testa limpeza de mensagens processadas."""
    mock_message_cache.clear_expired.return_value = EXPECTED_DELETED_COUNT

    result = await message_cache.cleanup_processed_messages()

    assert result == EXPECTED_DELETED_COUNT
    mock_message_cache.clear_expired.assert_called_once()


async def test_set_with_ttl_message_cache(message_cache, mock_message_cache):
    """Testa se mensagens são armazenadas com TTL."""
    mock_message_cache.exists.return_value = False

    await message_cache.is_message_processed('msg_123')

    # Verifica se set foi chamado com TTL
    call_args, call_kwargs = mock_message_cache.set.call_args
    assert call_kwargs.get('ttl_seconds') == DEFAULT_TTL_SECONDS
