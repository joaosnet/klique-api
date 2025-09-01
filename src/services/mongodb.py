import os

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

load_dotenv()

# Variáveis de ambiente do do Banco de Dados dos Usuários e Pontos de Interesse
DB_CONNECTION = os.getenv('DB_CONNECTION')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_DATABASE = os.getenv('DB_DATABASE')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_DNS = os.getenv('DB_DNS')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID_ANDROID')
MAILSLURP_API_KEY = os.getenv('MAILSLURP_API_KEY')


# Configuração das URLs de conexão
def get_mongodb_url(db: str = DB_DATABASE, host: str = DB_HOST) -> str:
    if DB_USERNAME and DB_PASSWORD:
        return f'{DB_CONNECTION}://{DB_USERNAME}:{DB_PASSWORD}@{host}:{DB_PORT}/{db}?authSource=admin'
    else:
        return f'{DB_CONNECTION}://{host}:{DB_PORT}/{db}?authSource=admin'

# Cliente e banco de dados para conexões
_client: AsyncIOMotorClient = None


def get_client() -> AsyncIOMotorClient:
    global _client  # noqa: PLW0603
    if _client is None:
        _client = AsyncIOMotorClient(get_mongodb_url())
    return _client

# Dependency injection para bancos de dados
def get_db() -> AsyncIOMotorDatabase:
    return get_client().get_database('klique')


# Coleções do banco de dados usando dependency injection
def get_users_collection():
    return get_db().get_collection('user')


def get_profiles_collection():
    return get_db().get_collection('profile')