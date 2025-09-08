"""Dependências específicas para webhooks."""

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from .database import get_db
from .services.gemini import GeminiService, get_gemini_service
from .services.whatsapp import WhatsAppService, get_whatsapp_service


class WebhookDependencies:
    """Classe para agrupar as dependências do webhook."""

    def __init__(
        self,
        gemini_service: GeminiService,
        whatsapp_service: WhatsAppService,
        db: AsyncIOMotorDatabase,
    ):
        self.gemini_service = gemini_service
        self.whatsapp_service = whatsapp_service
        self.db = db


def get_webhook_dependencies(
    gemini_service: GeminiService = Depends(get_gemini_service),
    whatsapp_service: WhatsAppService = Depends(get_whatsapp_service),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> WebhookDependencies:
    """Função de dependência para o webhook."""
    return WebhookDependencies(
        gemini_service=gemini_service,
        whatsapp_service=whatsapp_service,
        db=db,
    )
