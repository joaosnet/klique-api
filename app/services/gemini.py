from google import genai
from google.genai import types

from ..config import GOOGLE_API_KEY
from ..logger import logger


class GeminiService:
    def __init__(self, api_key: str = GOOGLE_API_KEY):
        if not api_key:
            raise ValueError('A chave da API do Gemini não foi fornecida.')
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-2.5-flash-image-preview'

    async def generate_image_from_prompt(self, prompt: str) -> bytes | None:
        """
        Generates an image from a text prompt using the Gemini API,
          following the
        client.models.generate_content_stream pattern.
        """
        logger.info(f'Generating image for prompt: {prompt}')

        contents = [
            types.Content(
                role='user', parts=[types.Part.from_text(text=prompt)]
            )
        ]
        generate_content_config = types.GenerateContentConfig(
            response_modalities=['IMAGE', 'TEXT']
        )

        try:
            # Segue o padrão do exemplo de código para uma chamada mais direta
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
                    and chunk.candidates[0].content.parts[0].inline_data
                    and chunk.candidates[0].content.parts[0].inline_data.data
                ):
                    logger.success('Image generated successfully')
                    return (
                        chunk.candidates[0].content.parts[0].inline_data.data
                    )

            logger.warning(
                'No image data found in Gemini response.{}'.format(
                    chunk
                )
            )
            return None

        except Exception as e:
            # Adiciona um log mais detalhado para o erro
            logger.error(
                f'An error occurred while generating the image with model '
                f'{self.model_name}: {e}'
            )
            return None


async def get_gemini_service() -> GeminiService:
    """Factory function to get an instance of GeminiService."""
    return GeminiService()
