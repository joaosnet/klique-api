from types import SimpleNamespace

import pytest

from app.services import image_generation


class FakeGeneratedImage:
    def __init__(self):
        self.cookies = {'session': 'ok'}
        self.save_calls = []

    async def save(self, **kwargs):
        self.save_calls.append(kwargs)
        return kwargs['filename']


class FakeWebImage:
    def __init__(self):
        self.save_calls = []

    async def save(self, **kwargs):
        self.save_calls.append(kwargs)
        return kwargs['filename']


class FakeGeminiClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    async def generate_content(self, prompt, files=None):
        self.calls.append({'prompt': prompt, 'files': files})
        return self.response


@pytest.mark.asyncio
async def test_generate_and_save_image_uses_generated_image_save(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(image_generation, 'MEDIA_DIR', str(tmp_path))
    fake_image = FakeGeneratedImage()
    client = FakeGeminiClient(SimpleNamespace(images=[fake_image], text='ok'))

    result = await image_generation.generate_and_save_image(
        prompt='um tabuleiro de xadrez futurista',
        output_dir='cards',
        filename='card-1',
        gemini_client=client,
        force=True,
    )

    assert result == 'cards/card-1.png'
    assert len(client.calls) == 1
    assert client.calls[0]['files'] is None
    assert (
        'Generate an original image based on the following description.'
        in client.calls[0]['prompt']
    )
    assert fake_image.save_calls == [
        {
            'path': str(tmp_path / 'cards'),
            'filename': 'card-1.png',
            'full_size': True,
        }
    ]


@pytest.mark.asyncio
async def test_generate_and_save_image_uses_existing_source_image_for_edit(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(image_generation, 'MEDIA_DIR', str(tmp_path))
    cards_dir = tmp_path / 'cards'
    cards_dir.mkdir(parents=True, exist_ok=True)
    source_path = cards_dir / 'card-2.png'
    source_path.write_bytes(b'img')

    fake_image = FakeGeneratedImage()
    client = FakeGeminiClient(SimpleNamespace(images=[fake_image], text='ok'))

    result = await image_generation.improve_image_with_ai(
        output_dir='cards',
        filename='card-2',
        style_prompt='mais contraste e atmosfera noir',
        base_prompt='Cena estratégica num restaurante elegante',
        gemini_client=client,
    )

    assert result == 'cards/card-2.png'
    assert client.calls[0]['files'] == [str(source_path)]
    assert (
        'Edit the provided image and return a newly generated image.'
        in client.calls[0]['prompt']
    )


@pytest.mark.asyncio
async def test_generate_and_save_image_uses_first_image_when_no_generated_image(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(image_generation, 'MEDIA_DIR', str(tmp_path))
    fake_image = FakeWebImage()
    client = FakeGeminiClient(SimpleNamespace(images=[fake_image], text='ok'))

    result = await image_generation.generate_and_save_image(
        prompt='um retrato editorial',
        output_dir='avatars',
        filename='user-1',
        gemini_client=client,
        force=True,
    )

    assert result == 'avatars/user-1.png'
    assert fake_image.save_calls == [
        {
            'path': str(tmp_path / 'avatars'),
            'filename': 'user-1.png',
        }
    ]


@pytest.mark.asyncio
async def test_generate_and_save_image_returns_cached_path_without_calling_client(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(image_generation, 'MEDIA_DIR', str(tmp_path))
    domains_dir = tmp_path / 'domains'
    domains_dir.mkdir(parents=True, exist_ok=True)
    cached_file = domains_dir / 'finance.png'
    cached_file.write_bytes(b'cached')

    client = FakeGeminiClient(SimpleNamespace(images=[], text='unused'))

    result = await image_generation.generate_and_save_image(
        prompt='algo',
        output_dir='domains',
        filename='finance',
        gemini_client=client,
        force=False,
    )

    assert result == 'domains/finance.png'
    assert client.calls == []


def test_prompt_builders_create_consistent_direction():
    domain_prompt = image_generation.build_domain_image_prompt('negociação')
    card_prompt = image_generation.build_card_image_prompt(
        'duas pessoas em tensão social'
    )
    avatar_prompt = image_generation.build_avatar_image_prompt(
        'homem de 30 anos confiante'
    )
    style_prompt = image_generation.build_style_improvement_prompt(
        'cena editorial',
        'mais textura e luz lateral',
    )

    assert 'Sem texto' in domain_prompt
    assert 'estratégia' in domain_prompt
    assert 'tensão estratégica' in card_prompt
    assert 'foco no rosto' in avatar_prompt
    assert 'Refina a imagem' in style_prompt