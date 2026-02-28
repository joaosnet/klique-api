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
