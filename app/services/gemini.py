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
        # Aprimora o prompt usando o serviço Gemini
        prompt = await self.enhance_prompt(prompt)

        logger.info(f'Gerando imagem para o prompt aprimorado: {prompt}')

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
                'Nenhum dado de imagem encontrado na '
                'resposta do Gemini.{}'.format(response_stream)
            )
            return None

        except Exception as e:
            logger.error(
                f'Ocorreu um erro ao gerar a imagem com o modelo '
                f'{self.model_name}: {e}'
            )
            return None

    async def enhance_prompt(self, prompt: str) -> str:
        """
        Aprimora o prompt do usuário usando o modelo gemini-2.5-flash-lite.

        Args:
            prompt (str): O prompt original do usuário.

        Returns:
            str: O prompt aprimorado ou o original em caso de erro.
        """
        if not prompt:
            logger.warning(
                'O prompt está vazio. Retornando o prompt original.'
            )
            return prompt

        try:
            # Configura o modelo específico para aprimoramento de prompts
            enhancement_model = self.client.models.get('gemini-2.5-flash-lite')

            # Cria o prompt aprimorado com instruções claras
            instrucoes_iniciais = """Melhore o seguinte prompt para gerar uma imagem mais detalhada '
                'e visualmente rica: """  # noqa: E501
            instrucoes = """
- Uma edição por prompt: não empilhe instruções no mesmo prompt, o modelo se confunde.

- Seja específico como um contratante: dê direções claras e detalhadas, como se estivesse contratando os serviços de alguém, sendo bem específico: “a pessoa à esquerda de boné…”

- Itere sem medo: a qualidade não piora ao longo das edições, então comece simples e vá refinando.

- Fale naturalmente: “remova o logo” e “pinte o moletom de roxo” funcionam perfeitamente."""  # noqa: E501
            enhancement_prompt = (
                instrucoes_iniciais + instrucoes + f"prompt: '{prompt}'"
            )

            # Gera o conteúdo usando o modelo de aprimoramento
            response = enhancement_model.generate_content(
                contents=[
                    types.Content(
                        role='user',
                        parts=[types.Part.from_text(text=enhancement_prompt)],
                    )
                ]
            )

            # Extrai o texto aprimorado da resposta
            if response.text:
                logger.info('Prompt aprimorado com sucesso.')
                return response.text
            else:
                logger.warning(
                    'Nenhum texto encontrado na resposta'
                    ' do modelo de aprimoramento.'
                )
                return prompt

        except Exception as e:
            logger.error(f'Erro ao aprimorar o prompt: {e}')
            return prompt


async def get_gemini_service() -> GeminiService:
    """Factory function to get an instance of GeminiService."""
    return GeminiService()
