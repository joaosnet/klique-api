from pathlib import Path

import pytest

from app.services.gemini_webapi_service import GeminiWebApiService

prompt1 = 'Fotografia de quadro escolar verde, sem nada escrito'

prompt2 = 'agora, escreva "Visualizacoes:" no canto superior desse quadro'


@pytest.mark.asyncio
async def test_generate_image_and_edit_it():
    """
    Testa a geração de uma imagem e sua posterior edição em múltiplos passos,
    mantendo o contexto da sessão.
    """
    service = GeminiWebApiService()
    generated_images_paths = []
    user_number = 'test_user_123'

    try:
        # Etapa 1: Gerar a imagem inicial do quadro

        chat = await service.get_or_create_chat(user_number)
        result1 = await service.generate_content_from_chat(prompt1, chat)
        assert result1 is not None
        assert isinstance(result1, list)
        assert len(result1) > 0

        image_bytes1 = result1[0]
        assert isinstance(image_bytes1, bytes)

        path1 = Path('generated_image_step1.png')
        with open(path1, 'wb') as f:
            f.write(image_bytes1)
        generated_images_paths.append(path1)

        # Etapa 2: Adicionar a primeira palavra ao quadro

        result2 = await service.generate_content_from_chat(prompt2, chat)
        assert result2 is not None
        assert isinstance(result2, list)
        assert len(result2) > 0

        image_bytes2 = result2[0]
        assert isinstance(image_bytes2, bytes)

        path2 = Path('generated_image_step2.png')
        with open(path2, 'wb') as f:
            f.write(image_bytes2)
        generated_images_paths.append(path2)

        # Etapa 3: Adicionar a segunda palavra ao quadro
        prompt3 = 'agora, adicione(escreva) "joão"'
        result3 = await service.generate_content_from_chat(prompt3, chat)
        assert result3 is not None
        assert isinstance(result3, list)
        assert len(result3) > 0

        image_bytes3 = result3[0]
        assert isinstance(image_bytes3, bytes)

        path3 = Path('generated_image_step3.png')
        with open(path3, 'wb') as f:
            f.write(image_bytes3)
        generated_images_paths.append(path3)

        # Verifica se a sessão foi mantida
        metadata = service.get_user_session_metadata(user_number)
        assert metadata is not None

    finally:
        # Limpa as imagens geradas após o teste
        for path in generated_images_paths:
            if path.exists():
                path.unlink()
        # Fecha o serviço
        await service.close()
