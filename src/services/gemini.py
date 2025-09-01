import asyncio
from gemini_webapi import GeminiClient
from typing import Optional
from PIL import Image
import tempfile
import os
from src.logger import logger

class GeminiService:
    def __init__(self, secure_1psid: str, secure_1psidts: str):
        """
        Inicializa o GeminiService com um cliente Gemini.
        As credenciais devem ser fornecidas explicitamente.
        """
        logger.opt(colors=True).info(
            f"[GeminiService.__init__] <cyan>secure_1psid</cyan>: <yellow>{secure_1psid[:6]}...{secure_1psid[-4:] if secure_1psid else ''}</yellow> | <cyan>secure_1psidts</cyan>: <yellow>{secure_1psidts[:6]}...{secure_1psidts[-4:] if secure_1psidts else ''}</yellow>"
        )
        if not secure_1psid or not secure_1psidts:
            logger.error("[GeminiService.__init__] Credenciais ausentes!")
            raise ValueError("As credenciais 'secure_1psid' e 'secure_1psidts' são obrigatórias.")

        self.client = GeminiClient(
            secure_1psid=secure_1psid,
            secure_1psidts=secure_1psidts
        )
        logger.info("[GeminiService.__init__] GeminiClient inicializado.")

    async def start_chat(self):
        """
        Inicia uma nova sessão de chat usando o cliente existente.
        """
        return self.client.start_chat()

    async def send_message(self, chat, prompt: str, image: Optional[Image.Image] = None):
        """
        Envia uma mensagem para o chat, opcionalmente com uma imagem.

        :param chat: A sessão de chat ativa.
        :param prompt: O prompt de texto para enviar.
        :param image: Uma imagem PIL para incluir na mensagem (opcional).
        :return: A resposta do modelo.
        """
        logger.debug(f"[GeminiService.send_message] Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''} | Imagem: {'Sim' if image else 'Não'}")
        try:
            if image:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    image.save(tmp.name)
                    tmp_path = tmp.name
                
                try:
                    response = await chat.send_message(prompt, files=[tmp_path])
                finally:
                    os.remove(tmp_path)
                logger.debug("[GeminiService.send_message] Resposta recebida com imagem.")
                return response
            else:
                response = await chat.send_message(prompt)
                logger.debug("[GeminiService.send_message] Resposta recebida sem imagem.")
                return response
        except Exception as e:
            logger.error(f"[GeminiService.send_message] Erro ao enviar mensagem: {e}", exc_info=True)
            raise

    async def batch_generate_images(self, prompts: list[str], image: Image.Image):
        """
        Gera imagens em lote para uma lista de prompts e uma única imagem.
        """
        logger.debug(f"[GeminiService.batch_generate_images] Lote de {len(prompts)} prompts recebido.")
        
        chat = await self.start_chat()
        
        tasks = [self.send_message(chat, prompt, image) for prompt in prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.debug("[GeminiService.batch_generate_images] Processamento em lote concluído.")
        return results
