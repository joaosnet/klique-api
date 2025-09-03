from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from src.config import DB_DATABASE, MONGO_URL


class DataBase:
    client: MongoClient | None = None
    db: Database | None = None


db = DataBase()


def get_client() -> MongoClient:
    if db.client is None:
        raise Exception('Database client not initialized')
    return db.client


def get_db() -> Database:
    if db.db is None:
        raise Exception('Database not initialized')
    return db.db


def connect_to_mongo():
    """Connects to MongoDB and initializes the client and db."""
    db.client = MongoClient(MONGO_URL)
    db.db = db.client[DB_DATABASE]


def close_mongo_connection():
    """Closes the MongoDB connection."""
    if db.client:
        db.client.close()


def get_users_collection() -> Collection:
    """Returns the 'users' collection."""
    return get_db()['users']


def get_profiles_collection() -> Collection:
    """Returns the 'profiles' collection."""
    return get_db()['profiles']


def get_mail_confirmation_collection() -> Collection:
    """Returns the 'mail_confirmation' collection."""
    return get_db()['mail_confirmation']
