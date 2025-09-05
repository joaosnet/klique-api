import asyncio
from functools import partial

from google import genai
from google.genai import types

from src.config import GOOGLE_API_KEY
from src.logger import logger


class GeminiService:
    def __init__(self, api_key: str = GOOGLE_API_KEY):
        if not api_key:
            raise ValueError('A chave da API do Gemini não foi fornecida.')
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-1.5-flash-preview'

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
            loop = asyncio.get_running_loop()
            func = partial(
                self.client.models.generate_content_stream,
                model=self.model_name,
                contents=contents,
                config=generate_content_config,
            )
            response_stream = await loop.run_in_executor(None, func)

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

            logger.warning('No image data found in Gemini response.')
            return None
        except Exception as e:
            logger.error(f'An error occurred while generating the image: {e}')
            return None


async def get_gemini_service() -> GeminiService:
    """Factory function to get an instance of GeminiService."""
    return GeminiService()
