import random

import httpx
from rich import print

from ..logger import logger

# A URL base do serviço go-whatsapp, acessível dentro da rede Docker.
# O nome do serviço é 'whatsapp', conforme definido no docker-compose.yml.
BASE_URL = 'http://whatsapp:3000'


# Mensagens criativas para uma melhor experiência do usuário
PROCESSING_MESSAGES = [
    'Ok, recebido! Deixa eu aquecer os motores aqui '
    'e já te mostro a mágica ✨',
    'Prompt na mão! Consultando os oráculos da criatividade... 🔮',
    'Entendido! Estou mergulhando nos pixels para '
    'criar algo incrível para você... 🎨',
]

FAILURE_MESSAGES = [
    'Hmm, parece que minha bola de '
    'cristal está um pouco embaçada com esse pedido. '
    'Que tal tentarmos com outras palavras? 🤔',
    'As musas da inspiração não colaboraram dessa vez.'
    ' Vamos tentar uma abordagem diferente? ✍️',
    'Opa! Tivemos um pequeno soluço criativo aqui. '
    'Pode me dar outra ideia para trabalhar?',
]


class WhatsAppService:
    """
    Serviço para interagir com a API REST do go-whatsapp.
    """

    _contacts_cache: dict[str, str] | None = None

    def __init__(self):
        """
        Inicializa o cliente HTTP assíncrono.
        """
        self.client = httpx.AsyncClient(base_url=BASE_URL)
        # As credenciais são 'admin:admin', conforme o docker-compose.yml
        self.auth = ('admin', 'admin')

    async def _send_image(
        self,
        *,
        phone: str,
        image_bytes: bytes,
        caption: str,
        filename: str,
    ):
        """Helper interno para envio de imagens (mensagem ou status)."""
        try:
            files = {'image': (filename, image_bytes, 'image/png')}
            data = {
                'phone': phone,
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
            response_data = response.json()
            print(
                f'[bold green]Imagem enviada para {phone}'
                ' com sucesso.[/bold green]'
            )
            return response_data
        except httpx.HTTPStatusError as e:
            logger.error(
                f'Erro HTTP ao enviar imagem p/{phone}: '
                f'{e.response.status_code} - {e.response.text}'
            )
        except Exception as e:
            logger.error(f'Erro inesperado ao enviar imagem p/{phone}: {e}')
        return None

    async def send_image_message(
        self, phone_number: str, image_bytes: bytes, caption: str = ''
    ):
        """
        Envia uma imagem para um número de telefone específico.

        :param phone_number: O número do destinatário (JID).
        :param image_bytes: A imagem em formato de bytes.
        :param caption: Uma legenda para a imagem (opcional).
        """
        # Refatorado para usar método interno
        return await self._send_image(
            phone=phone_number,
            image_bytes=image_bytes,
            caption=caption,
            filename='image.png',
        )

    @classmethod
    def get_random_processing_message(self) -> str:
        """Retorna uma mensagem de processamento aleatória."""
        return random.choice(PROCESSING_MESSAGES)

    @classmethod
    def get_random_failure_message(self) -> str:
        """Retorna uma mensagem de falha aleatória."""
        return random.choice(FAILURE_MESSAGES)

    async def send_message(
        self, phone_number: str, message: str
    ) -> str | None:
        """
        Envia uma mensagem de texto e retorna o ID da mensagem.

        :param phone_number: O número do destinatário (JID).
        :param message: A mensagem de texto a ser enviada.
        :return: O ID da mensagem enviada ou None em caso de erro.
        """
        try:
            # A opção "edit" permite que a mensagem seja editada ou deletada
            data = {
                'phone': phone_number,
                'message': message,
                'options': {'message': {'edit': None}},
            }

            response = await self.client.post(
                '/send/message',
                json=data,  # Usamos json em vez de data para o corpo aninhado
                auth=self.auth,
                timeout=30.0,
            )

            response.raise_for_status()
            response_data = response.json()
            message_id = response_data.get('data', {}).get('key', {}).get('id')

            if message_id:
                logger.info(f'Mensagem enviada com ID: {message_id}')
                return message_id

            logger.warning('Não foi possível obter o ID da mensagem enviada.')
            return None

        except httpx.HTTPStatusError as e:
            logger.error(
                'Erro ao enviar mensagem: '
                f'{e.response.status_code} - {e.response.text}'
            )
        except Exception as e:
            logger.error(f'Erro inesperado ao enviar mensagem: {e}')

        return None

    async def post_status_update(
        self, image_bytes: bytes, caption: str = ''
    ) -> str | None:
        """
        Posta uma imagem como uma atualização de status.

        :param image_bytes: A imagem em formato de bytes.
        :param caption: Uma legenda para o status (opcional).
        :return: O ID do status postado ou None em caso de erro.
        """
        response_data = await self._send_image(
            phone='status@broadcast',
            image_bytes=image_bytes,
            caption=caption,
            filename='status.png',
        )
        if response_data:
            return response_data.get('data', {}).get('key', {}).get('id')
        return None

    async def delete_status(self, status_id: str) -> bool:
        """
        Deleta um status específico.

        :param status_id: O ID do status a ser deletado.
        :return: True se foi deletado com sucesso, False caso contrário.
        """
        try:
            response = await self.client.delete(
                f'/status/{status_id}', auth=self.auth, timeout=30.0
            )
            response.raise_for_status()
            logger.info(f'Status {status_id} deletado com sucesso.')
            return True
        except httpx.HTTPStatusError as e:
            logger.error(
                f'Erro ao deletar status {status_id}: '
                f'{e.response.status_code} - {e.response.text}'
            )
        except Exception as e:
            logger.error(f'Erro inesperado ao deletar status {status_id}: {e}')

        return False

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

    async def get_contact_info(self, phone_number: str) -> dict | None:
        """
        Busca informações de um contato específico pelo número de telefone.

        Este método consulta a lista completa de contatos e filtra pelo número
        fornecido.

        :param phone_number: O número do telefone do contato (sem o sufixo @s.whatsapp.net).
        :return: Um dicionário com 'name' e 'number' do contato, ou None se não for encontrado.
        """  # noqa: E501
        try:
            logger.info(
                'Buscando informações do contato para '
                f'o número: {phone_number}'
            )
            response = await self.client.get(
                '/user/my/contacts', auth=self.auth, timeout=60.0
            )
            response.raise_for_status()
            response_data = response.json()
            logger.debug(f'Resposta dos contatos: {response_data}')
            contacts_list = response_data.get('results', {}).get('data', [])

            if isinstance(contacts_list, list):
                for contact in contacts_list:
                    jid = contact.get('jid', '')
                    # Extrai o número limpo do JID
                    # (ex: '5511999998888' de '5511999998888:1@s.whatsapp.net')
                    clean_number = jid.split('@')[0].split(':')[0]

                    if clean_number == phone_number:
                        name = contact.get('name')
                        if name:
                            logger.success(
                                f'Contato encontrado: {name} ({phone_number})'
                            )
                            return {'name': name, 'number': phone_number}

            logger.warning(
                f'Contato com número {phone_number} não encontrado na lista.'
            )
            return None

        except httpx.HTTPStatusError as e:
            logger.error(
                'Erro HTTP ao buscar contatos: '
                f'{e.response.status_code} - {e.response.text}'
            )
            return None
        except Exception as e:
            logger.error(
                f'Erro inesperado ao buscar informações do contato: {e}'
            )
            return None

    async def get_contact_avatar(self, phone: str) -> str | None:
        """
        Busca a URL do avatar de perfil do contato.

        :param phone: O número do telefone do contato.
        :return: URL da imagem de perfil ou None em caso de erro.
        """
        try:
            response = await self.client.get(
                f'/user/avatar?phone={phone}',
                auth=self.auth,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data.get(
                'avatar_url'
            )  # Assumindo que a resposta contém 'avatar_url'
        except httpx.HTTPStatusError as e:
            logger.error(
                f'Erro ao buscar avatar do contato {phone}: '
                f'{e.response.status_code} - {e.response.text}'
            )
        except Exception as e:
            logger.error(f'Erro inesperado ao buscar avatar {phone}: {e}')

        return None

    async def get_statuses(self) -> list[dict] | None:
        """
        Busca os status atuais do WhatsApp.

        :return: Lista de status ou None em caso de erro.
        """
        try:
            response = await self.client.get(
                '/status',
                auth=self.auth,
                timeout=30.0,
            )
            response.raise_for_status()
            data = response.json()
            return data.get('statuses', [])
        except httpx.HTTPStatusError as e:
            logger.error(
                f'Erro ao buscar status: '
                f'{e.response.status_code} - {e.response.text}'
            )
        except Exception as e:
            logger.error(f'Erro inesperado ao buscar status: {e}')

        return None

    async def edit_message(self, message_id: str, new_text: str) -> bool:
        """
        Edita uma mensagem existente usando o endpoint /message/:message_id/update.

        :param message_id: O ID da mensagem a ser editada.
        :param new_text: O novo texto da mensagem.
        :return: True se a edição foi bem-sucedida, False caso contrário.
        """  # noqa: E501
        try:
            data = {'text': new_text}

            response = await self.client.post(
                f'/message/{message_id}/update',
                json=data,
                auth=self.auth,
                timeout=30.0,
            )
            response.raise_for_status()
            logger.info(f'Mensagem {message_id} editada com sucesso.')
            return True
        except httpx.HTTPStatusError as e:
            logger.error(
                f'Erro ao editar mensagem {message_id}: '
                f'{e.response.status_code} - {e.response.text}'
            )
        except Exception as e:
            logger.error(
                f'Erro inesperado ao editar mensagem {message_id}: {e}'
            )

        return False

    async def close(self):
        """
        Fecha a sessão do cliente HTTP.
        """
        if self.client and not self.client.is_closed:
            await self.client.aclose()


def get_whatsapp_service() -> WhatsAppService:
    return WhatsAppService()
