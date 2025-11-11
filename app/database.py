from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi

from app.config import DB_DATABASE, get_mongodb_url

# Cliente e banco de dados para conexões
_client: AsyncMongoClient = None
_client_traducao: AsyncMongoClient = None


def get_client() -> AsyncMongoClient:
    global _client  # noqa: PLW0603
    if _client is None:
        mongo_url = get_mongodb_url()
        _client = AsyncMongoClient(
            mongo_url, server_api=ServerApi(version='1')
        )
    return _client


# Dependency injection para bancos de dados
def get_db():
    return get_client()[DB_DATABASE]


def close_db_connection():
    """
    Closes the MongoDB connection.
    """
    global _client, _client_traducao  # noqa: PLW0603
    if _client:
        _client.close()
        _client = None
    if _client_traducao:
        _client_traducao.close()
        _client_traducao = None


def get_password_recovery_collection():
    return get_db().get_collection('password_recovery')


def get_mail_confirmation_collection():
    return get_db().get_collection('mail_confirmation')


def get_users_collection():
    return get_db().get_collection('user')


def get_profiles_collection():
    return get_db().get_collection('profile')


def get_status_views_collection():
    return get_db().get_collection('status_views')


def get_cache_collection():
    return get_db().get_collection('cache')


def get_user_sessions_collection():
    return get_db().get_collection('user_sessions')


def get_status_images_collection():
    return get_db().get_collection('status_images')


def get_processed_messages_collection():
    return get_db().get_collection('processed_messages')


def get_status_generation_rate_limit_collection():
    return get_db().get_collection('status_generation_rate_limit')


def get_status_recent_viewers_collection():
    return get_db().get_collection('status_recent_viewers')
