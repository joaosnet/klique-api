"""Dependências específicas para webhooks."""

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from .database import get_db
from .services.protocols import ImageGenerationServiceProtocol
from .services.shared import AppServices
from .services.whatsapp import WhatsAppService


class WebhookDependencies:
    """Classe para agrupar as dependências do webhook."""

    def __init__(
        self,
        image_generation_service: ImageGenerationServiceProtocol,
        whatsapp_service: WhatsAppService,
        db: AsyncIOMotorDatabase,
    ):
        self.image_generation_service = image_generation_service
        self.whatsapp_service = whatsapp_service
        self.db = db


def get_webhook_dependencies(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> WebhookDependencies:
    """Função de dependência para o webhook."""
    return WebhookDependencies(
        image_generation_service=AppServices.get_image_generation_service(),
        whatsapp_service=AppServices.get_whatsapp_service(),
        db=db,
    )
