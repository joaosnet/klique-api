from typing import Any

from ..config import GEMINI_SERVICE_PROVIDER
from .gemini import GeminiService
from .gemini_webapi_service import GeminiWebApiService
from .whatsapp import WhatsAppService


class AppServices:
    """
    Contêiner para instâncias de serviços compartilhados na aplicação.
    Evita a recriação de clientes e conexões a cada requisição.
    """

    _whatsapp_service: WhatsAppService | None = None
    _image_generation_service: Any | None = None

    @classmethod
    def get_image_generation_service(cls) -> Any:
        """
        Retorna a instância do serviço de geração de imagem selecionado.
        Cria a instância se ela ainda não existir, com base na configuração.
        """
        if cls._image_generation_service is None:
            if GEMINI_SERVICE_PROVIDER.upper() == 'GEMINI_WEBAPI':
                cls._image_generation_service = GeminiWebApiService()
            else:
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
