from google import genai
from google.genai import types

from ..config import GOOGLE_API_KEY
from ..logger import logger

MODEL = 'gemini-2.5-flash-image-preview'


class GeminiService:
    def __init__(self, api_key: str = GOOGLE_API_KEY):
        if not api_key:
            raise ValueError('A chave da API do Gemini não foi fornecida.')
        self.client = genai.Client(api_key=api_key)
        self.model_name = MODEL

    async def generate_image_from_prompt(
        self, prompt: str, input_image: bytes | None = None
    ) -> bytes | None:
        """
        Generates an image from a text prompt using the Gemini API,
          following the
        client.models.generate_content_stream pattern.
        """
        if not prompt:
            logger.warning('O prompt está vazio. Retornando None.')
            return None

        logger.info(f'Gerando imagem para o prompt: {prompt}')

        parts = [types.Part.from_text(text=prompt)]
        if input_image:
            try:
                # Direct conversion to a Part with blob data
                image_part = types.Part(
                    inline_data=types.Blob(
                        mime_type='image/png', data=input_image
                    )
                )
                parts.append(image_part)
            except Exception as e:
                logger.error(f'Erro ao processar a imagem de entrada: {e}')
                return None

        contents = [types.Content(role='user', parts=parts)]
        generate_content_config = types.GenerateContentConfig(
            response_modalities=['IMAGE']
        )

        try:
            response_stream = self.client.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
                config=generate_content_config,
            )

            for chunk in response_stream:
                if (
                    chunk.candidates
                    and chunk.candidates[0].content
                    and chunk.candidates[0].content.parts
                ):
                    for part in chunk.candidates[0].content.parts:
                        if part.inline_data and part.inline_data.data:
                            logger.success('Imagem gerada com sucesso.')
                            return part.inline_data.data

            logger.warning(
                'Nenhum dado de imagem encontrado na resposta do Gemini.{}'
                .format(response_stream)
            )
            return None

        except Exception as e:
            logger.error(
                f'Ocorreu um erro ao gerar a imagem com o modelo '
                f'{self.model_name}: {e}'
            )
            return None


async def get_gemini_service() -> GeminiService:
    """Factory function to get an instance of GeminiService."""
    return GeminiService()
