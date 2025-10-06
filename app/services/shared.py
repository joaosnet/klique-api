from typing import Any

from .gemini import GeminiService
from .whatsapp import WhatsAppService


class AppServices:
    """
    Contêiner para instâncias de serviços compartilhados na aplicação.
    Evita a recriação de clientes e conexões a cada requisição.
    """

    _whatsapp_service: WhatsAppService | None = None
    _image_generation_service: Any | None = None

    @classmethod
    def get_image_generation_service(cls) -> GeminiService:
        """
        Retorna a instância do serviço de geração de imagem (Gemini oficial).
        O serviço Gemini Web API agora roda como servidor MCP separado.
        """
        if cls._image_generation_service is None:
            cls._image_generation_service = GeminiService()
        return cls._image_generation_service

    @classmethod
    def get_whatsapp_service(cls) -> WhatsAppService:
        """
        Retorna a instância singleton do WhatsAppService.
        Cria a instância se ela ainda não existir.
        """
        if cls._whatsapp_service is None:
            cls._whatsapp_service = WhatsAppService()
        return cls._whatsapp_service
