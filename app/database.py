from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi

from .config import DB_DATABASE, get_mongodb_url

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


async def close_db_connection():
    """
    Fecha a conexão com o MongoDB de forma assíncrona.
    """
    global _client, _client_traducao  # noqa: PLW0603
    if _client:
        await _client.close()
        _client = None
    if _client_traducao:
        await _client_traducao.close()
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


def get_otp_collection():
    return get_db().get_collection('otp')


def get_magic_links_collection():
    return get_db().get_collection('magic_links')


def get_webauthn_challenges_collection():
    return get_db().get_collection('webauthn_challenges')


def get_status_generation_rate_limit_collection():
    return get_db().get_collection('status_generation_rate_limit')


def get_status_recent_viewers_collection():
    return get_db().get_collection('status_recent_viewers')


def get_user_credits_collection():
    """Collection para armazenar saldo de créditos dos usuários."""
    return get_db().get_collection('user_credits')


def get_payment_transactions_collection():
    """Collection para armazenar transações de pagamento PIX."""
    return get_db().get_collection('payment_transactions')


def get_link_analytics_collection():
    """Collection para rastrear views de preview (OG) e cliques em links."""
    return get_db().get_collection('link_analytics')


# ========================================
# OmniFlash Collections
# ========================================


def get_domains_collection():
    """Collection para domínios de treino do usuário."""
    return get_db().get_collection('domains')


def get_domain_images_collection():
    """Collection para cache global de imagens de domínio (por tema)."""
    return get_db().get_collection('domain_images')


def get_scenario_cards_collection():
    """Collection para cards de cenário gerados e salvos."""
    return get_db().get_collection('scenario_cards')


def get_reviews_collection():
    """Collection para estado de revisão SRS por card/usuário."""
    return get_db().get_collection('reviews')


def get_simulation_logs_collection():
    """Collection para logs de sessões de treino SRS."""
    return get_db().get_collection('simulation_logs')
