import asyncio
from io import BytesIO
from typing import Optional

from gemini_webapi import GeminiClient
from PIL import Image

from src.config import SECURE_1PSID, SECURE_1PSIDTS


class GeminiAppService:
    """
    Serviço para interagir com a API do Gemini para gerar imagens.
    """

    def __init__(self):
        """
        Inicializa o cliente Gemini.
        """
        self.client = GeminiClient(
            secure_1psid=SECURE_1PSID, secure_1psidts=SECURE_1PSIDTS
        )
        self.loop = asyncio.get_event_loop()

    async def generate_image_from_prompt(self, prompt: str) -> Optional[bytes]:
        """
        Gera uma imagem a partir de um prompt de texto.

        Args:
            prompt: O prompt de texto para a geração da imagem.

        Returns:
            Os bytes da imagem gerada em formato PNG, ou None se falhar.
        """
        try:
            await self.client.init()
            chat = self.client.start_chat()

            full_prompt = f"gere uma imagem sobre: {prompt}"

            response = await chat.send_message(full_prompt)

            if response.images:
                img_data = response.images[0]
                image = Image.open(BytesIO(img_data))
                buffer = BytesIO()
                image.save(buffer, format='PNG')
                return buffer.getvalue()

        except Exception as e:
            print(f'Erro ao gerar imagem com o Gemini: {e}')

        return None
