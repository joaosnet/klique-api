import os
import tempfile
from typing import Any, Dict

import httpx
from gemini_webapi import GeminiClient

from ..config import SECURE_1PSID, SECURE_1PSIDTS
from ..logger import logger


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

        self.client = GeminiClient(
            secure_1psid, secure_1psidts or '', proxy=None
        )
        self.is_initialized = False
        self._user_chats: Dict[str, Any] = {}

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

    async def get_or_create_chat(self, user_number: str):
        """
        Obtém uma sessão de chat existente para um usuário ou cria uma nova.

        Conforme a documentação oficial, o client.start_chat() pode receber
        metadata de sessões anteriores para continuar conversas.

        Args:
            user_number (str): O número do usuário para identificar a sessão.

        Returns:
            ChatSession: A sessão de chat para o usuário.
        """
        await self._initialize_client()

        if user_number in self._user_chats:
            logger.info(
                f'Sessão de chat reutilizada para o usuário {user_number}.'
            )
            # Reutiliza sessão anterior com metadata
            return self.client.start_chat(
                metadata=self._user_chats[user_number]
            )

        logger.info(
            f'Criando nova sessão de chat para o usuário {user_number}.'
        )
        chat = self.client.start_chat()
        # Armazena metadados da sessão para reutilização futura
        if hasattr(chat, 'metadata'):
            self._user_chats[user_number] = chat.metadata
        return chat

    @staticmethod
    def _prepare_prompt(prompt: str) -> str:
        """
        Prepara o prompt adicionando instrução de geração se necessário.

        Conforme a documentação, o Gemini por padrão envia imagens da web
        a menos que seja especificamente solicitado para 'gerar' imagens.
        """
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

        if not any(prompt_lower.startswith(kw) for kw in generate_keywords):
            return f'Generate an image of {prompt}'
        return prompt

    @staticmethod
    def _prepare_temp_files(input_images: list[bytes]) -> list[str]:
        """Cria arquivos temporários para as imagens de entrada."""
        temp_file_paths = []
        for i, image_bytes in enumerate(input_images):
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=f'_{i}.png'
            ) as temp_file:
                temp_file.write(image_bytes)
                temp_file_paths.append(temp_file.name)
        return temp_file_paths

    @staticmethod
    def _cleanup_temp_files(temp_file_paths: list[str]) -> None:
        """Remove arquivos temporários."""
        for path in temp_file_paths:
            try:
                os.unlink(path)
            except OSError:
                pass

    @staticmethod
    async def _extract_image_bytes(image) -> bytes | None:
        """Extrai bytes de uma imagem da resposta."""
        try:
            # Cria arquivo temporário para salvar a imagem
            with tempfile.NamedTemporaryFile(
                suffix='.png', delete=False
            ) as temp_file:
                temp_path = temp_file.name

            try:
                # Usa o método correto da API conforme documentação
                await image.save(
                    path=os.path.dirname(temp_path),
                    filename=os.path.basename(temp_path),
                )

                # Lê os bytes do arquivo salvo
                with open(temp_path, 'rb') as f:
                    image_bytes = f.read()

                logger.debug(f'Imagem salva com {len(image_bytes)} bytes')
                return image_bytes

            finally:
                # Remove o arquivo temporário
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass

        except Exception as e:
            logger.error(f'Erro ao extrair bytes da imagem: {e}')
            # Fallback: usar URL da imagem
            if hasattr(image, 'url'):
                try:
                    async with httpx.AsyncClient() as client:
                        response_img = await client.get(image.url)
                        return response_img.content
                except Exception as url_error:
                    logger.error(f'Erro ao baixar imagem via URL: {url_error}')
            return None

    async def _generate_with_session(
        self,
        prompt: str,
        chat,
        input_images: list[bytes] | None = None,
    ) -> list[bytes] | None:
        """
        Gera conteúdo usando uma sessão de chat existente.

        Args:
            prompt: O prompt para geração.
            chat: Sessão de chat já inicializada.
            input_images: Lista de bytes das imagens de entrada (opcional).

        Returns:
            list[bytes] | None: Lista de bytes das imagens geradas, ou None.
        """
        try:
            prompt = self._prepare_prompt(prompt)
            logger.info(f'Enviando prompt para a web API: "{prompt}"')

            temp_file_paths = []
            files = []

            if input_images:
                temp_file_paths = self._prepare_temp_files(input_images)
                files = temp_file_paths
                logger.info(f'Carregadas {len(files)} imagens de entrada.')

            try:
                response = await chat.send_message(prompt, files=files)
                logger.success('Conteúdo gerado com sucesso pela web API.')

                if not response.images:
                    logger.warning('Nenhuma imagem retornada na resposta')
                    return None

                generated_images = []
                for i, image in enumerate(response.images):
                    logger.debug(
                        f'Processando imagem {i + 1}/{len(response.images)}'
                    )
                    image_bytes = await self._extract_image_bytes(image)
                    if image_bytes:
                        logger.info(
                            f'🖼️ Imagem {i + 1} extraída com sucesso '
                            f'({len(image_bytes)} bytes)'
                        )
                        generated_images.append(image_bytes)
                    else:
                        logger.warning(
                            f'Falha ao extrair bytes da imagem {i + 1}'
                        )

                if generated_images:
                    logger.success(
                        f'Total de {len(generated_images)} '
                        'imagens processadas com sucesso'
                    )
                return generated_images or None

            finally:
                self._cleanup_temp_files(temp_file_paths)

        except Exception as e:
            logger.error(f'Erro ao gerar conteúdo com a web API: {e}')
            return None

    async def generate_content_from_chat(
        self,
        prompt: str,
        chat: Any,
        input_images: list[bytes] | None = None,
    ) -> list[bytes] | None:
        """
        Gera conteúdo usando uma sessão de chat específica do usuário.

        Args:
            prompt (str): O prompt para a geração.
            chat (Any): A sessão de chat do usuário.
            input_images (list[bytes], optional): As imagens de entrada.

        Returns:
            list[bytes] | None: Lista de bytes das imagens geradas, ou None.
        """
        result = await self._generate_with_session(
            prompt, chat, input_images=input_images
        )

        # Atualiza os metadados da sessão se possível
        user_number = self._extract_user_number_from_chat(chat)
        if user_number and hasattr(chat, 'metadata'):
            self._user_chats[user_number] = chat.metadata

        return result

    async def generate_status_caption(
        self,
        chat: Any,
        image_prompt: str | None = None,
        user_name: str | None = None,
    ) -> str | None:
        """
        Gera uma legenda criativa e com quebra de padrão para status do WhatsApp
        usando a mesma sessão de chat da imagem gerada.

        Args:
            chat (Any): A sessão de chat do usuário (mesma da imagem).
            image_prompt (str, optional): O prompt original usado para gerar a imagem.
            user_name (str, optional): Nome do usuário para personalização.

        Returns:
            str | None: Legenda criativa gerada ou None em caso de erro.
        """  # noqa: E501
        try:
            # Constrói o prompt para gerar a legenda criativa
            caption_prompt = self._build_caption_prompt(
                image_prompt, user_name
            )

            logger.info(
                'Gerando legenda criativa para status via Gemini Web API'
            )

            # Usa a mesma sessão de chat para manter contexto
            response = await chat.send_message(caption_prompt)

            if response and response.text:
                caption = response.text.strip()
                logger.success(
                    f'Legenda gerada com sucesso: "{caption[:50]}..."'
                )
                return caption

            logger.warning('Resposta vazia ao gerar legenda para status')
            return None

        except Exception as e:
            logger.error(f'Erro ao gerar legenda para status: {e}')
            return None

    @staticmethod
    def _build_caption_prompt(
        image_prompt: str | None = None, user_name: str | None = None
    ) -> str:
        """
        Constrói o prompt para gerar legenda criativa para status.

        Args:
            image_prompt (str, optional): O prompt original da imagem.
            user_name (str, optional): Nome do usuário.

        Returns:
            str: Prompt otimizado para geração de legenda.
        """
        base_prompt = (
            'Agora crie uma legenda criativa e '
            'com quebra de padrão para esta imagem '
            'que será postada como status no WhatsApp. A legenda deve ser:\n\n'
            '• Criativa e original, fugindo do óbvio\n'
            '• Quebrar padrões e expectativas\n'
            '• Provocativa ou intrigante\n'
            '• Máximo 2-3 linhas\n'
            '• Pode usar emojis estrategicamente\n'
            '• Deve gerar engajamento e curiosidade\n'
            "• Evite clichês como 'arte é vida', "
            "'criatividade sem limites', etc.\n\n"
        )

        if image_prompt:
            context_prompt = (
                'Baseando-se na imagem que acabamos de criar'
                f" com o tema '{image_prompt}', "
            )
        else:
            context_prompt = 'Baseando-se na imagem que acabamos de criar, '

        if user_name:
            personalization = (
                'A legenda pode incluir uma referência sutil'
                f' ao {user_name} se fizer sentido. '
            )
        else:
            personalization = ''

        return (
            base_prompt
            + context_prompt
            + personalization
            + 'Crie APENAS a legenda, sem explicações adicionais.'
        )

    @staticmethod
    def _extract_user_number_from_chat(chat) -> str | None:
        """Extrai o user_number do chat ou metadata."""
        user_number = getattr(chat, 'user_number', None)
        if user_number:
            return user_number

        if not hasattr(chat, 'metadata'):
            return None

        metadata = chat.metadata
        if isinstance(metadata, dict):
            return metadata.get('user_number')
        elif isinstance(metadata, list) and metadata:
            first_item = metadata[0]
            if isinstance(first_item, dict):
                return first_item.get('user_number')
            elif hasattr(first_item, 'user_number'):
                return getattr(first_item, 'user_number')
        return None

    def reset_user_session(self, user_number: str):
        """
        Reseta a sessão de chat para um usuário específico.

        Args:
            user_number (str): O número do usuário a ter a sessão resetada.
        """
        if user_number in self._user_chats:
            del self._user_chats[user_number]
            logger.info(f'Sessão de chat para {user_number} foi resetada.')
        else:
            logger.info(
                f'Nenhuma sessão de chat encontrada para {user_number}'
            )

    def get_user_session_metadata(
        self, user_number: str
    ) -> Dict[str, Any] | None:
        """
        Retorna os metadados da sessão para um usuário específico.

        Args:
            user_number (str): O número do usuário.

        Returns:
            Dict[str, Any] | None: Metadados da sessão ou None.
        """
        return self._user_chats.get(user_number)

    async def close(self):
        """
        Fecha a sessão do cliente Gemini.

        Conforme a documentação, é importante fechar o cliente adequadamente
        para liberar recursos.
        """
        if self.is_initialized and self.client:
            try:
                await self.client.close()
                self.is_initialized = False
                self._user_chats.clear()  # Limpa cache de sessões
                logger.info('Cliente GeminiWebApi fechado com sucesso.')
            except Exception as e:
                logger.error(f'Erro ao fechar cliente GeminiWebApi: {e}')
                self.is_initialized = False


async def get_gemini_webapi_service() -> GeminiWebApiService:
    """Factory function para obter uma instância de GeminiWebApiService."""
    return GeminiWebApiService()
