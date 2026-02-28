import os
from typing import Any, Optional

from bson import ObjectId
from google.genai import types

from ..database import (
    get_domain_images_collection,
    get_domains_collection,
    get_scenario_cards_collection,
)
from ..logger import logger

MEDIA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'generated_media'
)


async def generate_and_save_image(
    prompt: str,
    output_dir: str,
    filename: str,
    gemini_client: Any,
    force: bool = False,
) -> Optional[str]:
    """
    Usa a Gemini API oficial (Imagen) para gerar uma imagem.
    Retorna o path relativo da imagem (ex: 'domains/dating.png') se sucesso.
    Se force=True, ignora o cache e regenera a imagem.
    """
    os.makedirs(os.path.join(MEDIA_DIR, output_dir), exist_ok=True)
    base_name = filename.rsplit('.', 1)[0]
    expected_path = os.path.join(MEDIA_DIR, output_dir, f'{base_name}.png')

    if not force and os.path.exists(expected_path):
        logger.debug(f'Imagem já gerada em cache local: {expected_path}')
        return f'{output_dir}/{base_name}.png'

    try:
        logger.info(f'Gerando imagem via Gemini Imagen para: {prompt[:50]}...')
        response = await gemini_client.aio.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type='image/png',
            ),
        )

        if not response.generated_images:
            logger.warning(
                f'Imagen não retornou imagens para o prompt: {prompt[:50]}'
            )
            return None

        image_bytes = response.generated_images[0].image.image_bytes
        if not image_bytes:
            logger.warning(f'Imagem vazia retornada para: {prompt[:50]}')
            return None

        with open(expected_path, 'wb') as f:
            f.write(image_bytes)

        logger.success(f'Imagem gerada e salva: {expected_path}')
        return f'{output_dir}/{base_name}.png'

    except Exception as e:
        logger.error(f'Erro ao gerar imagem: {e}')

    return None


async def get_or_generate_domain_image(
    theme: str, gemini_client: Any, force: bool = False
) -> Optional[str]:
    """
    Verifica se a imagem deste tema de domínio já existe no cache (shared db).
    Se existir, retorna o url.
    Se não, gera usando gemini_webapi, salva localmente e na DB, e retorna.
    """
    col = get_domain_images_collection()
    cached = await col.find_one({'theme': theme})

    if not force and cached and cached.get('image_url'):
        abs_url = cached['image_url']
        # Propagate to any domain docs that still lack image_url
        # (e.g. newly created domain whose theme already has a cached image)
        domains_col = get_domains_collection()
        await domains_col.update_many(
            {'theme': theme, 'image_url': None},
            {'$set': {'image_url': abs_url}},
        )
        return abs_url

    prompt = (
        'Cria uma ilustração 3D incrivelmente atmosférica, '
        'cinematográfica e high-end '
        f"do conceito '{theme}'. Usa um tema visual que simbolize "
        'estratégia e teoria dos jogos, '
        'com um toque de tecnologia futurista subtil, iluminação '
        'de estúdio dramática (chiaroscuro) '
        'e um objeto simbólico central '
        '(ex: xadrez, escalas, mapa holográfico, cartas). '
        'Qualidade super premium, hiper detalhado, sem texto na imagem.'
    )

    path = await generate_and_save_image(
        prompt=prompt,
        output_dir='domains',
        filename=theme,
        gemini_client=gemini_client,
        force=force,
    )

    if path:
        abs_url = f'/media/{path}'
        await col.update_one(
            {'theme': theme},
            {'$set': {'image_url': abs_url, 'theme': theme}},
            upsert=True,
        )
        # Propagate image_url to all domain docs with this theme
        domains_col = get_domains_collection()
        await domains_col.update_many(
            {'theme': theme},
            {'$set': {'image_url': abs_url}},
        )
        logger.info(f'image_url propagado para domínios com tema "{theme}"')
        return abs_url

    return None


async def get_or_generate_card_image(
    card_id: str, visual_prompt: str, gemini_client: Any, force: bool = False
) -> Optional[str]:
    """
    Gera uma imagem para um card específico baseado na ideia
    sugerida pelo oráculo.
    """
    prompt = (
        f'{visual_prompt}. A imagem deve ter qualidade fotorealista de alto '
        'nível, '
        'cinematográfica, iluminação dramática, simbolizando o dilema '
        'estratégico do '
        'cenário em questão. Sem texto na imagem.'
    )

    path = await generate_and_save_image(
        prompt=prompt,
        output_dir='cards',
        filename=card_id,
        gemini_client=gemini_client,
        force=force,
    )

    if path:
        abs_url = f'/media/{path}'
        # Salva o URL no card associado
        if not card_id.startswith('demo-'):
            col = get_scenario_cards_collection()
            await col.update_one(
                {'_id': ObjectId(card_id)}, {'$set': {'media_urls': [abs_url]}}
            )
        return abs_url

    return None


async def improve_image_with_ai(
    output_dir: str,
    filename: str,
    style_prompt: str,
    base_prompt: str,
    gemini_client: Any,
) -> Optional[str]:
    """
    Melhora uma imagem existente usando a IA.

    Tenta passar a imagem atual ao Gemini com instruções de estilo.
    Se não for suportado, faz fallback gerando uma nova imagem com o
    base_prompt + style_prompt combinados.

    Returns o path relativo da nova imagem ou None em caso de falha.
    """
    combined_prompt = (
        f'{base_prompt}. Aplica o seguinte estilo artístico: {style_prompt}. '
        'Mantém a qualidade cinematográfica, fotorealista, sem texto na imagem.'
    )
    return await generate_and_save_image(
        prompt=combined_prompt,
        output_dir=output_dir,
        filename=filename,
        gemini_client=gemini_client,
        force=True,
    )


async def init_demo_images(gemini_client: Any) -> None:
    """Gera imagens para as cartas e domínios da demonstração."""
    import asyncio  # noqa: PLC0415

    from loguru import logger  # noqa: PLC0415

    themes = {
        'office': 'Dinâmicas de Escritório corporativo, política interna',
        'finance': 'Negociação Salarial, mercado financeiro de alto risco',
        'dating': (
            'Atracção e Status, encontro romântico num lounge elegante'
        ),
    }

    cards = {
        'demo-1': 'Um ambiente de negócios corporativo tenso '
        'durante uma avaliação',
        'demo-2': 'Espera num restaurante elegante com luz baixa, solitário',
        'demo-3': 'Trabalho em equipa no escritório sendo apresentado à '
        'diretoria',
    }

    logger.info('Iniciando geração de mockups do modo Demo...')

    for theme, desc in themes.items():
        prompt = (
            'Cria uma ilustração 3D incrivelmente atmosférica, '
            'cinematográfica e high-end '
            f"do conceito '{desc}'. Usa um tema visual que simbolize "
            'estratégia e teoria dos jogos, '
            'com um toque de tecnologia futurista subtil, iluminação '
            'de estúdio dramática (chiaroscuro) '
            'e um objeto simbólico central. Sem texto na imagem.'
        )
        await generate_and_save_image(prompt, 'domains', theme, gemini_client)
        await asyncio.sleep(2)  # Previne rate limits

    for card_id, desc in cards.items():
        prompt = (
            f'{desc}. A imagem deve ter qualidade fotorealista de alto '
            'nível, '
            'cinematográfica, iluminação dramática, simbolizando o dilema '
            'estratégico do '
            'cenário em questão. Sem texto na imagem.'
        )
        await generate_and_save_image(prompt, 'cards', card_id, gemini_client)
        await asyncio.sleep(2)
