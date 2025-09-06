from contextlib import asynccontextmanager

from app.database import close_db_connection, get_client

from .whatsapp import WhatsAppService


class AppServices:
    """
    Contêiner para instâncias de serviços compartilhados na aplicação.
    Evita a recriação de clientes e conexões a cada requisição.
    """

    _whatsapp_service: WhatsAppService | None = None

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
        Fecha as conexões abertas pelos serviços, como o cliente HTTP e o banco de dados.
        """
        if cls._whatsapp_service:
            await cls._whatsapp_service.close()
            cls._whatsapp_service = None
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
