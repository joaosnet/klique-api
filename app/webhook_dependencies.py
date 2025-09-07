"""Dependências específicas para webhooks."""

from fastapi import Depends

from .cache import (
    MessageCache,
    StatusImageCache,
    get_message_cache,
    get_status_image_cache,
)
from .services.gemini import GeminiService, get_gemini_service
from .services.whatsapp import WhatsAppService, get_whatsapp_service


class WebhookDependencies:
    """Classe para agrupar as dependências do webhook."""

    def __init__(
        self,
        gemini_service: GeminiService,
        whatsapp_service: WhatsAppService,
        status_image_cache: StatusImageCache,
        message_cache: MessageCache,
    ):
        self.gemini_service = gemini_service
        self.whatsapp_service = whatsapp_service
        self.status_image_cache = status_image_cache
        self.message_cache = message_cache


def get_webhook_dependencies(
    gemini_service: GeminiService = Depends(get_gemini_service),
    whatsapp_service: WhatsAppService = Depends(get_whatsapp_service),
    status_image_cache: StatusImageCache = Depends(get_status_image_cache),
    message_cache: MessageCache = Depends(get_message_cache),
) -> WebhookDependencies:
    """Função de dependência para o webhook."""
    return WebhookDependencies(
        gemini_service=gemini_service,
        whatsapp_service=whatsapp_service,
        status_image_cache=status_image_cache,
        message_cache=message_cache,
    )
