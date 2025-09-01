import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    # Configurações do Gemini
    GEMINI_1PSID: str = ""
    GEMINI_1PSIDTS: str = ""
    GEMINI_TIMEOUT: float = 30.0
    GEMINI_AUTO_CLOSE: bool = False
    GEMINI_CLOSE_DELAY: float = 300.0
    GEMINI_CONCURRENCY_LIMIT: int = 4

    # Configurações do Firebase e Google Drive
    MONGO_DB_CONNECTION_STRING: str
    GOOGLE_DRIVE_SHARED_FOLDER_ID: str
    FIREBASE_CREDENTIALS_JSON: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    GOOGLE_DRIVE_ROOT_FOLDER_ID: str

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()