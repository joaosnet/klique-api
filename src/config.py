import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator


class Settings(BaseSettings):
    # Configurações do Gemini
    GEMINI_TIMEOUT: float = 30.0
    GEMINI_AUTO_CLOSE: bool = False
    GEMINI_CLOSE_DELAY: float = 300.0
    GEMINI_CONCURRENCY_LIMIT: int = 4

    # Configurações do Firebase e Google Drive
    MONGO_DB_CONNECTION_STRING: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    GOOGLE_DRIVE_ROOT_FOLDER_ID: str

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("MONGO_DB_CONNECTION_STRING", mode="after")
    def add_direct_connection(cls, v: str) -> str:
        """Adiciona directConnection=true à URI do MongoDB se não estiver presente."""
        if "directConnection=true" not in v:
            return f"{v}&directConnection=true"
        return v


settings = Settings()