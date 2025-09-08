import io
import os
import time
from pathlib import Path

import pytest
from PIL import Image
from rich import print

from app.services.gemini import GeminiService, get_gemini_service


@pytest.fixture
async def service():
    return await get_gemini_service()


def _save_test_image(image_bytes: bytes, filename: str):
    """Salva a imagem de teste se os bytes forem válidos."""
    if not image_bytes:
        return
    output_dir = Path('temp')
    output_dir.mkdir(exist_ok=True)
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.save(output_dir / filename)
    except Exception:
        # Não falha o teste se a imagem não puder ser salva,
        # mas a validação principal falhará.
        pass


@pytest.mark.skipif(
    not os.getenv('GOOGLE_API_KEY'),
    reason='GOOGLE_API_KEY não está configurada',
)
class TestGeminiServiceIntegration:
    @staticmethod
    def test_init_without_api_key_raises_error():
        """
        Testa se um ValueError é levantado quando
        a chave da API não é fornecida.
        """
        with pytest.raises(
            ValueError, match='A chave da API do Gemini não foi fornecida'
        ):
            GeminiService(api_key=None)

    @staticmethod
    @pytest.mark.asyncio
    async def test_generate_content_from_prompt_success(
        service: GeminiService,
    ):
        """Testa a geração de conteúdo bem-sucedida a partir de um prompt."""
        prompt = (
            'A hyper-realistic 4k image of a '
            'cat programming in a neon-lit room'
        )
        time.sleep(10)  # Evitar rate limiting da API
        start_time = time.monotonic()
        image_bytes = await service.generate_content(prompt)
        end_time = time.monotonic()
        print(
            f'\n[bold green]Tempo de geração (prompt):[/bold green] '
            f'{end_time - start_time:.2f}s'
        )

        assert image_bytes is not None
        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 0

        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                assert img.format is not None
        except Exception as e:
            pytest.fail(f'A imagem gerada não é válida: {e}')

        _save_test_image(
            image_bytes, 'test_generate_content_from_prompt_success.png'
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_generate_content_with_input_image_success(
        service: GeminiService,
    ):
        """
        Testa a geração de conteúdo bem-sucedida com uma imagem de entrada.
        """
        prompt = 'Add a futuristic helmet to this cat'

        input_img_byte_arr = io.BytesIO()
        Image.new('RGB', (100, 100), color='red').save(
            input_img_byte_arr, format='PNG'
        )
        input_image_bytes = input_img_byte_arr.getvalue()

        time.sleep(10)  # Evitar rate limiting da API
        start_time = time.monotonic()
        image_bytes = await service.generate_content(
            prompt, input_image=input_image_bytes
        )
        end_time = time.monotonic()
        print(
            f'\n[bold blue]Tempo de geração (prompt+imagem):[/bold blue] '
            f'{end_time - start_time:.2f}s'
        )

        assert image_bytes is not None
        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 0

        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                assert img.format is not None
        except Exception as e:
            pytest.fail(f'A imagem gerada a partir de outra não é válida: {e}')

        _save_test_image(
            image_bytes, 'test_generate_content_with_input_image_success.png'
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_generate_content_empty_prompt_returns_none(
        service: GeminiService,
    ):
        """Testa se um prompt vazio para generate_content retorna None."""
        image_bytes = await service.generate_content('')
        assert image_bytes is None

    @staticmethod
    @pytest.mark.asyncio
    async def test_enhance_prompt_success(service: GeminiService):
        """Testa se o aprimoramento de prompt funciona."""
        prompt = 'a cat'
        time.sleep(5)  # Evitar rate limiting
        enhanced_prompt = await service.enhance_prompt(prompt)
        assert enhanced_prompt is not None
        assert isinstance(enhanced_prompt, str)
        # O modelo pode retornar o mesmo prompt se já for bom o suficiente
        assert len(enhanced_prompt) > 0
        print(f'\nPrompt original: "{prompt}"')
        print(f'Prompt aprimorado: "{enhanced_prompt}"')

    @staticmethod
    @pytest.mark.asyncio
    async def test_enhance_prompt_empty_returns_original(
        service: GeminiService,
    ):
        """Testa se um prompt vazio para enhance_prompt retorna o original."""
        enhanced_prompt = await service.enhance_prompt('')
        assert not enhanced_prompt


@pytest.mark.asyncio
async def test_get_gemini_service():
    """Testa se o factory get_gemini_service funciona."""
    if os.getenv('GOOGLE_API_KEY'):
        service = await get_gemini_service()
        assert isinstance(service, GeminiService)
    else:
        with pytest.raises(
            ValueError, match='A chave da API do Gemini não foi fornecida'
        ):
            await get_gemini_service()
