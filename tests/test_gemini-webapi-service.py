from pathlib import Path

import pytest

from app.services.gemini_webapi_service import GeminiWebApiService


@pytest.mark.asyncio
async def test_generate_image_and_edit_it():
    """
    Testa a geração de uma imagem e sua posterior edição em múltiplos passos,
    mantendo o contexto da sessão.
    """
    service = GeminiWebApiService()
    generated_images_paths = []

    try:
        # Etapa 1: Gerar a imagem inicial do quadro
        prompt1 = 'Fotografia de quadro escolar verde, sem nada escrito'
        image_bytes1 = await service.generate_content(prompt1)
        assert image_bytes1 is not None
        assert isinstance(image_bytes1, bytes)

        path1 = Path('generated_image_step1.png')
        with open(path1, 'wb') as f:
            f.write(image_bytes1)
        generated_images_paths.append(path1)

        # Etapa 2: Adicionar a primeira palavra ao quadro
        prompt2 = (
            'agora, escreva "Visualizacoes:" no canto superior desse quadro'
        )
        image_bytes2 = await service.generate_content(prompt2)
        assert image_bytes2 is not None
        assert isinstance(image_bytes2, bytes)

        path2 = Path('generated_image_step2.png')
        with open(path2, 'wb') as f:
            f.write(image_bytes2)
        generated_images_paths.append(path2)

        # Etapa 3: Adicionar a segunda palavra ao quadro
        prompt3 = 'agora, adicione(escreva) "joão"'
        image_bytes3 = await service.generate_content(prompt3)
        assert image_bytes3 is not None
        assert isinstance(image_bytes3, bytes)

        path3 = Path('generated_image_step3.png')
        with open(path3, 'wb') as f:
            f.write(image_bytes3)
        generated_images_paths.append(path3)

        # Verifica se a sessão foi mantida
        metadata = service.get_session_metadata()
        assert metadata is not None

    finally:
        # Limpa as imagens geradas após o teste
        for path in generated_images_paths:
            if path.exists():
                path.unlink()
