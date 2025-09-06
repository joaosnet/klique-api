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
    async def test_generate_image_from_prompt_success(service: GeminiService):
        """Testa a geração de imagem bem-sucedida
        a partir de um prompt de texto."""
        prompt = (
            'A hyper-realistic 4k image of a '
            'cat programming in a neon-lit room'
        )
        start_time = time.monotonic()
        image_bytes = await service.generate_image_from_prompt(prompt)
        end_time = time.monotonic()
        print(
            f'\n[bold green]Tempo de geração (prompt):[/bold green] '
            f'{end_time - start_time:.2f}s'
        )

        assert image_bytes is not None
        assert isinstance(image_bytes, bytes)
        assert len(image_bytes) > 0

        # Verifica se os bytes correspondem a uma imagem válida
        try:
            with Image.open(io.BytesIO(image_bytes)) as img:
                assert img.format is not None
        except Exception as e:
            pytest.fail(f'A imagem gerada não é válida: {e}')

        _save_test_image(
            image_bytes, 'test_generate_image_from_prompt_success.png'
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_generate_image_with_input_image_success(
        service: GeminiService,
    ):
        """
        Testa a geração de imagem bem-sucedida a
          partir de um prompt e uma imagem de entrada.
        """
        prompt = 'Add a futuristic helmet to this cat'

        # Cria uma imagem de entrada simples
        input_img_byte_arr = io.BytesIO()
        Image.new('RGB', (100, 100), color='red').save(
            input_img_byte_arr, format='PNG'
        )
        input_image_bytes = input_img_byte_arr.getvalue()

        start_time = time.monotonic()
        image_bytes = await service.generate_image_from_prompt(
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
            image_bytes, 'test_generate_image_with_input_image_success.png'
        )

    @staticmethod
    @pytest.mark.asyncio
    async def test_generate_image_empty_prompt_returns_none(
        service: GeminiService,
    ):
        """Testa se um prompt vazio retorna None."""
        image_bytes = await service.generate_image_from_prompt('')
        assert image_bytes is None


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
