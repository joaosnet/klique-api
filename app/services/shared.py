from contextlib import asynccontextmanager
from typing import Any

from app.database import close_db_connection, get_client

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

    @classmethod
    async def close_services(cls) -> None:
        """
        Fecha as conexões abertas pelos serviços,
        como o cliente HTTP e o banco de dados.
        """
        if cls._whatsapp_service:
            await cls._whatsapp_service.close()
            cls._whatsapp_service = None

        # Limpa o serviço de geração de imagem também
        if cls._image_generation_service:
            cls._image_generation_service = None
        close_db_connection()


@asynccontextmanager
async def lifespan(_):
    """
    Gerenciador de ciclo de vida do FastAPI para inicializar e
    encerrar os serviços da aplicação.
    """
    # Inicializa o cliente do banco de dados no startup
    get_client()
    # Serviços são inicializados sob demanda (lazy)
    yield
    # Encerra os serviços ao finalizar a aplicação
    await AppServices.close_services()
