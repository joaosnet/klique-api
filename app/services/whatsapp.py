import httpx
from rich import print

from ..logger import logger

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

        :param phone_number: O número do destinatário (JID).
        :param image_bytes: A imagem em formato de bytes.
        :param caption: Uma legenda para a imagem (opcional).
        """
        try:
            # Conforme a documentação,
            # o endpoint /send/image espera multipart/form-data.
            files = {'image': ('image.png', image_bytes, 'image/png')}
            data = {
                'phone': phone_number,
                'caption': caption,
                'view_once': 'false',
                'compress': 'false',
                'is_forwarded': 'false',
            }

            response = await self.client.post(
                '/send/image',
                data=data,
                files=files,
                auth=self.auth,
                timeout=30.0,
            )

            response.raise_for_status()
            print(
                '[bold green]Imagem enviada com sucesso para '
                f'{phone_number}.[/bold green]'
            )
            return response.json()

        except httpx.HTTPStatusError as e:
            print(
                '[bold red]Erro ao enviar imagem: '
                f'{e.response.status_code}[/bold red]'
            )
            print(f'Resposta da API: {e.response.text}')
        except Exception as e:
            print(
                f'[bold red]Erro inesperado ao enviar imagem: {e}[/bold red]'
            )

        return None

    async def send_text_message(self, phone_number: str, message: str):
        """
        Envia uma mensagem de texto para um número de telefone específico.

        :param phone_number: O número do destinatário (JID).
        :param message: A mensagem de texto a ser enviada.
        """
        try:
            data = {
                'phone': phone_number,
                'message': message,
            }

            response = await self.client.post(
                '/send/message',
                data=data,
                auth=self.auth,
                timeout=30.0,
            )

            response.raise_for_status()
            print(
                '[bold green]Mensagem de texto enviada com sucesso para '
                f'{phone_number}.[/bold green]'
            )
            return response.json()

        except httpx.HTTPStatusError as e:
            print(
                '[bold red]Erro ao enviar mensagem de texto: '
                f'{e.response.status_code}[/bold red]'
            )
            print(f'Resposta da API: {e.response.text}')
        except Exception as e:
            print(
                '[bold red]Erro inesperado ao enviar '
                f'mensagem de texto: {e}[/bold red]'
            )

        return None

    async def post_status_update(self, image_bytes: bytes, caption: str = ''):
        """
        Posta uma imagem como uma atualização de
        status usando o endpoint send/image
        com o destinatário especial status@broadcast.

        :param image_bytes: A imagem em formato de bytes.
        :param caption: Uma legenda para o status (opcional).
        """
        try:
            # Para status do WhatsApp,
            # usamos o destinatário especial status@broadcast
            files = {'image': ('status.png', image_bytes, 'image/png')}
            data = {
                'phone': 'status@broadcast',
                'caption': caption,
                'view_once': 'false',
                'compress': 'false',
                'is_forwarded': 'false',
            }

            response = await self.client.post(
                '/send/image',
                data=data,
                files=files,
                auth=self.auth,
                timeout=30.0,
            )
            response.raise_for_status()
            print('[bold green]Status postado com sucesso![/bold green]')
            return response.json()
        except httpx.HTTPStatusError as e:
            print(
                '[bold red]Erro ao postar status:'
                f' {e.response.status_code}[/bold red]'
            )
            print(f'Resposta da API: {e.response.text}')
        except Exception as e:
            print(
                f'[bold red]Erro inesperado ao postar status: {e}[/bold red]'
            )

        return None

    async def download_media(self, media_path: str) -> bytes | None:
        """Faz o download de um arquivo de mídia do go-whatsapp."""
        if not self.client:
            return None

        media_url = f'{BASE_URL}/{media_path}'
        try:
            response = await self.client.get(media_url)
            response.raise_for_status()
            return response.content
        except httpx.HTTPStatusError as e:
            logger.error(f'Erro de status ao baixar mídia de {media_url}: {e}')
            return None
        except Exception as e:
            logger.error(f'Erro inesperado ao baixar mídia: {e}')
            return None

    async def close(self):
        """
        Fecha a sessão do cliente HTTP.
        """
        await self.client.aclose()
