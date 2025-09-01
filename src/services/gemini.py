from gemini_webapi import GeminiClient
from typing import Optional
from PIL import Image
import tempfile
import os
from dotenv import dotenv_values
class GeminiService:
    def __init__(self):
        """
        Inicializa o GeminiService com um cliente Gemini.
        Os cookies são carregados automaticamente pelo browser-cookie3.
        """
        config = dotenv_values(".env")
        self.client = GeminiClient(
            secure_1psid=config["Secure_1PSID"],
            secure_1psidts=config["Secure_1PSIDTS"]
        )

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
        if image:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                image.save(tmp.name)
                tmp_path = tmp.name
            
            try:
                response = await chat.send_message(prompt, files=[tmp_path])
            finally:
                os.remove(tmp_path)
            return response
        else:
            return await chat.send_message(prompt)
