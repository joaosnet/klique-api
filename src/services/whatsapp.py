import base64

import httpx
from rich import print

# A URL base do serviço go-whatsapp, acessível dentro da rede Docker.
# O nome do serviço é 'whatsapp', conforme definido no docker-compose.yml.
BASE_URL = 'http://whatsapp:3000'


class WhatsAppService:
    """
    Serviço para interagir com a API REST do go-whatsapp.
    """

    def __init__(self):
        """
        Inicializa o cliente HTTP assíncrono.
        """
        self.client = httpx.AsyncClient(base_url=BASE_URL)
        # As credenciais são 'admin:admin', conforme o docker-compose.yml
        self.auth = ('admin', 'admin')

    async def send_image_message(
        self, phone_number: str, image_bytes: bytes, caption: str = ''
    ):
        """
        Envia uma imagem para um número de telefone específico.

        :param phone_number: O número do destinatário.
        :param image_bytes: A imagem em formato de bytes.
        :param caption: Uma legenda para a imagem (opcional).
        """
        try:
            # A imagem precisa ser enviada em base64.
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')

            payload = {
                'phone': phone_number,
                'image': f'data:image/png;base64,{image_base64}',
                'caption': caption,
            }

            response = await self.client.post(
                '/messages/image', json=payload, auth=self.auth, timeout=30.0
            )

            response.raise_for_status()
            print(
                f'[bold green]Imagem enviada com sucesso para {phone_number}.[/bold green]'
            )
            return response.json()

        except httpx.HTTPStatusError as e:
            print(
                f'[bold red]Erro ao enviar imagem: {e.response.status_code}[/bold red]'
            )
            print(e.response.text)
        except Exception as e:
            print(
                f'[bold red]Erro inesperado ao enviar imagem: {e}[/bold red]'
            )

        return None

    async def close(self):
        """
        Fecha a sessão do cliente HTTP.
        """
        await self.client.aclose()
