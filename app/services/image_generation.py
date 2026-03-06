import asyncio
import os
from typing import Any, Optional
from bson import ObjectId

from ..config import GEMINI_CONCURRENCY_LIMIT
from ..database import (
    get_domain_images_collection,
    get_domains_collection,
    get_scenario_cards_collection,
)
from ..logger import logger

MEDIA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    'generated_media',
)
IMAGE_GENERATION_SEMAPHORE = asyncio.Semaphore(
    max(1, GEMINI_CONCURRENCY_LIMIT)
)

IMAGE_NEGATIVE_PROMPT = (
    'Sem texto, sem tipografia, sem legendas, sem watermark, '
    'sem interface, sem colagens, sem múltiplos painéis.'
)


def _get_image_output_path(output_dir: str, filename: str) -> tuple[str, str]:
    base_name = filename.rsplit('.', 1)[0]
    expected_path = os.path.join(MEDIA_DIR, output_dir, f'{base_name}.png')
    return base_name, expected_path


def _build_image_request_prompt(
    prompt: str, source_image_path: str | None = None
) -> str:
    cleaned_prompt = prompt.strip()
    if source_image_path:
        return (
            'Edit the provided image and return a newly generated image. '
            'Do not search for, send, or reuse web images.\n\n'
            f'{cleaned_prompt}'
        )

    return (
        'Generate an original image based on the following description. '
        'Do not search for, send, or reuse web images.\n\n'
        f'{cleaned_prompt}'
    )


def build_domain_image_prompt(theme: str) -> str:
    return (
        'Cria uma ilustração conceitual premium com estética 3D editorial, '
        'cinematográfica e atmosférica para representar o domínio '
        f"'{theme}'. Composição limpa, um único símbolo central forte, "
        'iluminação dramática de estúdio, profundidade elegante, materiais '
        'sofisticados, detalhes de alto nível e um subtil tom futurista. '
        'A imagem deve transmitir estratégia, decisão, poder e leitura social. '
        f'{IMAGE_NEGATIVE_PROMPT}'
    )


def build_card_image_prompt(visual_prompt: str) -> str:
    return (
        f'{visual_prompt}. Cria uma cena cinematográfica premium, '
        'fotorealista ou hiper-realista, com foco narrativo claro, um único '
        'momento dramático, linguagem visual editorial, profundidade de campo '
        'controlada, iluminação intencional e composição forte. A cena deve '
        'simbolizar tensão estratégica, consequência e leitura de contexto. '
        f'{IMAGE_NEGATIVE_PROMPT}'
    )


def build_avatar_image_prompt(prompt: str) -> str:
    return (
        f'{prompt}. Retrato premium de busto ou close-up, expressão natural, '
        'foco no rosto, enquadramento limpo, fundo simples e sofisticado, '
        'iluminação cinematográfica de estúdio, pele realista, aparência '
        'elegante, visual contemporâneo e alta definição. '
        f'{IMAGE_NEGATIVE_PROMPT}'
    )


def build_style_improvement_prompt(base_prompt: str, style_prompt: str) -> str:
    return (
        f'{base_prompt}. Refina a imagem com o seguinte direcionamento de '
        f'estilo: {style_prompt}. Preserva a identidade central da cena, '
        'melhora composição, luz, materiais, contraste, coerência visual e '
        'acabamento premium. '
        f'{IMAGE_NEGATIVE_PROMPT}'
    )


async def generate_and_save_image(
    prompt: str,
    output_dir: str,
    filename: str,
    gemini_client: Any,
    force: bool = False,
    source_image_path: str | None = None,
) -> Optional[str]:
    """
    Usa a GeminiWeb API para gerar uma imagem.
    Retorna o path relativo da imagem (ex: 'domains/dating.png') se sucesso.
    Se force=True, ignora o cache e regenera a imagem.
    """
    os.makedirs(os.path.join(MEDIA_DIR, output_dir), exist_ok=True)
    base_name, expected_path = _get_image_output_path(output_dir, filename)

    if not force and os.path.exists(expected_path):
        logger.debug(f'Imagem já gerada em cache local: {expected_path}')
        return f'{output_dir}/{base_name}.png'

    try:
        logger.info(f'Gerando imagem via GeminiWeb API para: {prompt[:50]}...')

        files = None
        if source_image_path and os.path.exists(source_image_path):
            files = [source_image_path]
        elif source_image_path:
            logger.warning(
                f'Imagem base não encontrada para edição: {source_image_path}'
            )

        request_prompt = _build_image_request_prompt(prompt, source_image_path)

        async with IMAGE_GENERATION_SEMAPHORE:
            response = await gemini_client.generate_content(
                request_prompt,
                files=files,
            )

        images = getattr(response, 'images', None) or []

        if not images:
            logger.warning(
                'Gemini não retornou imagens para o prompt: '
                f'{prompt[:50]}. Resposta textual: '
                f'{getattr(response, "text", "")[:160]}'
            )
            return None

        image = next(
            (candidate for candidate in images if hasattr(candidate, 'cookies')),
            images[0],
        )
        save_kwargs = {
            'path': os.path.join(MEDIA_DIR, output_dir),
            'filename': f'{base_name}.png',
        }
        if hasattr(image, 'cookies'):
            save_kwargs['full_size'] = True

        await image.save(**save_kwargs)

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

    prompt = build_domain_image_prompt(theme)

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
    prompt = build_card_image_prompt(visual_prompt)

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
    combined_prompt = build_style_improvement_prompt(
        base_prompt,
        style_prompt,
    )
    _, source_image_path = _get_image_output_path(output_dir, filename)
    return await generate_and_save_image(
        prompt=combined_prompt,
        output_dir=output_dir,
        filename=filename,
        gemini_client=gemini_client,
        force=True,
        source_image_path=source_image_path,
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
        prompt = build_domain_image_prompt(desc)
        await generate_and_save_image(prompt, 'domains', theme, gemini_client)
        await asyncio.sleep(2)  # Previne rate limits

    for card_id, desc in cards.items():
        prompt = build_card_image_prompt(desc)
        await generate_and_save_image(prompt, 'cards', card_id, gemini_client)
        await asyncio.sleep(2)
