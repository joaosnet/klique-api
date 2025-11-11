"""Dependências específicas para webhooks."""

from fastapi import Depends, Request

from .database import get_db
from .services.gemini import GeminiService
from .services.shared import AppServices
from .services.whatsapp import WhatsAppService


class WebhookDependencies:
    """Classe para agrupar as dependências do webhook."""

    def __init__(
        self,
        image_generation_service: GeminiService,
        whatsapp_service: WhatsAppService,
        db,
    ):
        self.image_generation_service = image_generation_service
        self.whatsapp_service = whatsapp_service
        self.db = db


def get_webhook_dependencies(
    request: Request,
    db=Depends(get_db),
) -> WebhookDependencies:
    """Função de dependência para o webhook."""
    # Usa o serviço de geração de imagem do 'app.state' se estiver definido
    # no 'lifespan'. Caso contrário, usa o serviço padrão.
    image_generation_service = getattr(
        request.app.state,
        'gemini_web_api_service',
        AppServices.get_image_generation_service(),
    )

    return WebhookDependencies(
        image_generation_service=image_generation_service,
        whatsapp_service=request.app.state.whatsapp_service,
        db=db,
    )
