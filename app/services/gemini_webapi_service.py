import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict

from gemini_webapi import GeminiClient

from ..config import SECURE_1PSID, SECURE_1PSIDTS
from ..logger import logger

DIRETORIO_TEMP = Path('temp')


class GeminiWebApiService:
    """
    Serviço para interagir com a API web do Gemini usando a biblioteca
    gemini-webapi.
    """

    def __init__(
        self,
        secure_1psid: str = SECURE_1PSID,
        secure_1psidts: str = SECURE_1PSIDTS,
    ):
        """
        Inicializa o cliente GeminiWebApi.

        Args:
            secure_1psid (str): Credencial __Secure-1PSID.
            secure_1psidts (str): Credencial __Secure-1PSIDTS (pode ser vazio).
        """
        if not secure_1psid:
            raise ValueError('A credencial SECURE_1PSID é obrigatória.')

        # Se browser-cookie3 estiver instalado, pode usar apenas GeminiClient()
        self.client = GeminiClient(
            secure_1psid, secure_1psidts or '', proxy=None
        )
        self.is_initialized = False
        self._current_chat = None
        self._chat_metadata = None

    async def _initialize_client(self):
        """Inicializa o cliente se ainda não estiver inicializado."""
        if not self.is_initialized:
            try:
                await self.client.init(
                    timeout=30,
                    auto_close=True,
                    close_delay=300,
                    auto_refresh=True,
                )
                self.is_initialized = True
                logger.info('Cliente GeminiWebApi inicializado com sucesso.')
            except Exception as e:
                msg = f'Falha ao inicializar o cliente GeminiWebApi: {e}'
                logger.error(msg)
                raise

    async def start_chat(self, metadata: Dict[str, Any] | None = None):
        """
        Inicia uma nova sessão de chat ou continua uma existente.

        Args:
            metadata (Dict[str, Any], optional): Metadados de uma sessão
                anterior para continuar a conversa.

        Returns:
            ChatSession: A sessão de chat iniciada.
        """
        await self._initialize_client()
        logger.info(
            'Iniciando uma nova sessão de chat da web API...'
            if not metadata
            else 'Continuando uma sessão de chat da web API...'
        )
        return self.client.start_chat(metadata=metadata)

    @classmethod
    async def _generate_with_session(
        self,
        prompt: str,
        chat,
        input_image: bytes | None = None,
    ) -> bytes | None:
        """
        Gera conteúdo usando uma sessão de chat existente.

        Args:
            prompt: O prompt para geração
            chat: Sessão de chat já inicializada
            input_image: Bytes da imagem de entrada (opcional)

        Returns:
            bytes | None: Bytes da imagem gerada ou None se não houver imagem
        """
        try:
            # Verifica se o prompt já instrui a gerar uma imagem
            prompt_lower = prompt.strip().lower()
            generate_keywords = [
                'gere',
                'crie',
                'faça',
                'desenhe',
                'generate',
                'create',
                'make',
                'draw',
            ]

            if not any(
                prompt_lower.startswith(keyword)
                for keyword in generate_keywords
            ):
                # Adiciona a instrução no início do prompt
                prompt = f'Gere uma imagem de {prompt}'

            logger.info(f'Enviando prompt para a web API: "{prompt}"')

            files = None
            temp_file_path = None

            # Se há uma imagem de entrada, salva temporariamente
            if input_image:
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix='.png'
                ) as temp_file:
                    temp_file.write(input_image)
                    temp_file_path = temp_file.name
                    files = [temp_file_path]

            try:
                response = await chat.send_message(prompt, files=files)
                logger.success('Conteúdo gerado com sucesso pela web API.')

                # Verifica se há imagens na resposta
                if response.images:
                    # Pega a primeira imagem gerada
                    image = response.images[0]

                    # Garante que o diretório temp existe
                    DIRETORIO_TEMP.mkdir(parents=True, exist_ok=True)

                    # Gera um nome único para a imagem

                    unique_filename = f'{uuid.uuid4()}.png'
                    image_path = DIRETORIO_TEMP / unique_filename

                    # Salva a imagem no DIRETORIO_TEMP
                    await image.save(
                        path=str(DIRETORIO_TEMP),
                        filename=unique_filename,
                    )

                    # Lê os bytes da imagem salva
                    with open(image_path, 'rb') as f:
                        image_bytes = f.read()

                    # Não remove o arquivo, pois foi salvo no DIRETORIO_TEMP
                    logger.info(f'Imagem salva em: {image_path}')

                    return image_bytes

                return None

            finally:
                # Remove arquivo temporário de entrada se foi criado
                if temp_file_path:
                    Path(temp_file_path).unlink(missing_ok=True)

        except Exception as e:
            logger.error(
                f'Erro ao gerar conteúdo com a web API do Gemini: {e}'
            )
            return None

    async def generate_content(
        self,
        prompt: str,
        input_image: bytes | None = None,
        use_persistent_session: bool = True,
    ) -> bytes | None:
        """
        Gera uma imagem a partir de um prompt, gerenciando a sessão de chat.

        Args:
            prompt: Prompt para geração de imagem
            input_image: Bytes da imagem de entrada para edição (opcional)
            use_persistent_session: Se deve usar sessão persistente
              para manter contexto

        Returns:
            bytes | None: Bytes da imagem gerada ou None em caso de erro
        """
        if use_persistent_session and self._current_chat is not None:
            chat = self._current_chat
        else:
            chat = await self.start_chat(
                metadata=self._chat_metadata
                if use_persistent_session
                else None
            )
            if use_persistent_session:
                self._current_chat = chat

        result = await self._generate_with_session(
            prompt, chat, input_image=input_image
        )

        # Salva os metadados da sessão para continuidade
        if use_persistent_session and hasattr(chat, 'metadata'):
            self._chat_metadata = chat.metadata

        return result

    def reset_session(self):
        """
        Reseta a sessão atual, forçando uma nova conversa na próxima chamada.
        """
        self._current_chat = None
        self._chat_metadata = None
        logger.info('Sessão de chat resetada.')

    def get_session_metadata(self) -> Dict[str, Any] | None:
        """
        Retorna os metadados da sessão atual.

        Returns:
            Dict[str, Any] | None: Metadados da sessão
            ou None se não houver sessão ativa
        """
        return self._chat_metadata


async def get_gemini_webapi_service() -> GeminiWebApiService:
    """Factory function para obter uma instância de GeminiWebApiService."""
    return GeminiWebApiService()


if __name__ == '__main__':
    import asyncio

    async def main():
        service = GeminiWebApiService()
        prompt = (
            'Uma pintura digital vibrante de um gato astronauta flutuando'
            ' no espaço, com estrelas brilhantes ao fundo.'
        )
        image_bytes = await service.generate_content(prompt)
        if image_bytes:
            with open('generated_image.png', 'wb') as f:
                f.write(image_bytes)
            print("Imagem gerada e salva como 'generated_image.png'")
        else:
            print('Falha ao gerar a imagem.')

    asyncio.run(main())
