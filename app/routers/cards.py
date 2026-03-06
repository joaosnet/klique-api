"""
Rotas para geração e gerenciamento de Scenario Cards.

O endpoint principal (/generate-stream) usa Server-Sent Events (SSE)
para gerar um card por vez via Gemini WebAPI, replicando o padrão
do christmas.py.
"""

import json
import os
import re
import shutil
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import StreamingResponse

from ..database import (
    get_domains_collection,
    get_reviews_collection,
    get_scenario_cards_collection,
)
from ..dependencies import get_current_active_user
from ..services.image_generation import (
    MEDIA_DIR,
    build_card_image_prompt,
    get_or_generate_card_image,
    improve_image_with_ai,
)
from .schemas import (
    DefautMessage,
    GenerateCardRequest,
    ImageImproveRequest,
    ScenarioCard,
    ScenarioCardUpdate,
    SwipeAction,
    SwipeResponse,
)

router = APIRouter(prefix='/api/cards', tags=['cards'])

# Caminho para os system prompts
_PROMPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'agents')


def _load_prompt(card_format: str) -> str:
    prompt_file_map = {
        'game_theory': 'omniflash_oracle_prompt.md',
        'concurso_certo_errado': 'concurso_ce_prompt.md',
        'concurso_multipla_escolha': 'concurso_me_prompt.md',
        'flashcard_basico': 'flashcard_basico_prompt.md',
    }
    filename = prompt_file_map.get(card_format, 'flashcard_basico_prompt.md')
    prompt_path = os.path.join(_PROMPTS_DIR, filename)

    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to a basic prompt or game theory if not found
        fallback = os.path.join(_PROMPTS_DIR, 'omniflash_oracle_prompt.md')
        if os.path.exists(fallback):
            with open(fallback, 'r', encoding='utf-8') as f:
                return f.read()
        return (
            'You are an AI generating study flashcards. '
            'Please output valid JSON matching the format.'
        )


async def generate_sse_event(event: str, data: dict) -> str:
    return f'event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n'


async def _card_generation_stream(
    domain_name: str,
    domain_theme: str,
    context: str | None,
    gemini_client,
    card_format: str = 'game_theory',
):
    """Async generator que produz eventos SSE para geração de um card."""
    try:
        yield await generate_sse_event(
            'progress',
            {
                'step': 1,
                'total': 3,
                'message': 'Consultando o Oráculo...',
                'percent': 20,
            },
        )

        oracle_prompt = _load_prompt(card_format)
        user_message = (
            f'Domínio: {domain_name}\n'
            f'Tema: {domain_theme}\n'
            f'Formato Desejado: {card_format}\n'
        )
        if context:
            user_message += f'Contexto adicional: {context}\n'

        full_prompt = f'{oracle_prompt}\n\n---\n\n{user_message}'

        yield await generate_sse_event(
            'progress',
            {
                'step': 2,
                'total': 3,
                'message': 'Gerando cenário tático...',
                'percent': 60,
            },
        )

        response = await gemini_client.generate_content(full_prompt)
        raw_text = response.text.strip()

        # Extrair JSON — remover blocos de código markdown se presentes
        json_match = re.search(r'\{[\s\S]*\}', raw_text)
        if not json_match:
            yield await generate_sse_event(
                'error',
                {
                    'message': 'Gemini não retornou JSON válido.'
                    ' Tente novamente.'
                },
            )
            return

        card_dict = json.loads(json_match.group(0))
        # Ensure card_format is set correctly
        card_dict['card_format'] = card_format

        yield await generate_sse_event(
            'progress',
            {
                'step': 3,
                'total': 3,
                'message': 'Cenário pronto.',
                'percent': 100,
            },
        )

        yield await generate_sse_event('complete', {'card': card_dict})

    except json.JSONDecodeError as e:
        yield await generate_sse_event(
            'error', {'message': f'Erro ao interpretar resposta da IA: {e}'}
        )
    except Exception as e:
        yield await generate_sse_event(
            'error', {'message': f'Erro interno: {e}'}
        )


@router.post('/generate-stream')
async def generate_card_stream(
    request: Request,
    body: GenerateCardRequest,
    current_user=Depends(get_current_active_user),
    domains_col=Depends(get_domains_collection),
):
    """
    Gera um único Scenario Card via SSE.

    O cliente recebe eventos 'progress', 'complete' ou 'error'.
    O card NÃO é salvo automaticamente — o usuário deve fazer swipe
    para salvá-lo via POST /api/cards/swipe.
    """
    user_id = str(current_user['_id'])

    try:
        oid = ObjectId(body.domain_id)
    except Exception:
        raise HTTPException(status_code=400, detail='ID de domínio inválido')

    domain = await domains_col.find_one({'_id': oid, 'user_id': user_id})
    if not domain:
        raise HTTPException(status_code=404, detail='Domínio não encontrado')

    gemini_client = getattr(request.app.state, 'gemini_webapi_client', None)
    if not gemini_client:
        raise HTTPException(
            status_code=503,
            detail=(
                'Motor de IA não está configurado. '
                'Verifique SECURE_1PSID no .env.'
            ),
        )

    async def stream_generator():
        async for chunk in _card_generation_stream(
            domain_name=domain['name'],
            domain_theme=domain['theme'],
            context=body.context,
            gemini_client=gemini_client,
            card_format=body.card_format,
        ):
            yield chunk

    return StreamingResponse(
        stream_generator(),
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
        },
    )


@router.post('/swipe', response_model=SwipeResponse)
async def swipe_card(  # noqa: PLR0913, PLR0917
    request: Request,
    body: SwipeAction,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_active_user),
    domains_col=Depends(get_domains_collection),
    cards_col=Depends(get_scenario_cards_collection),
    reviews_col=Depends(get_reviews_collection),
):
    """
    Processa a decisão de swipe do usuário.
    - action='save': persiste o card + cria registro de review inicial
    - action='discard': descarta silenciosamente
    """
    if body.action not in {'save', 'discard'}:
        raise HTTPException(
            status_code=400, detail="action deve ser 'save' ou 'discard'"
        )

    if body.action == 'discard':
        return SwipeResponse(success=True, message='Card descartado.')

    user_id = str(current_user['_id'])

    try:
        oid = ObjectId(body.domain_id)
    except Exception:
        raise HTTPException(status_code=400, detail='ID de domínio inválido')

    domain = await domains_col.find_one({'_id': oid, 'user_id': user_id})
    if not domain:
        raise HTTPException(status_code=404, detail='Domínio não encontrado')

    now = datetime.now(timezone.utc)
    card_doc = {
        'domain_id': body.domain_id,
        'user_id': user_id,
        'card_format': body.card_data.card_format,
        'template_type': body.card_data.template_type,
        'scenario_context': body.card_data.scenario_context,
        'question': body.card_data.question,
        'predicted_outcome': body.card_data.predicted_outcome,
        'game_theory_explanation': body.card_data.game_theory_explanation,
        'probability_heat_score': body.card_data.probability_heat_score,
        'visual_prompt_idea': body.card_data.visual_prompt_idea,
        'options': body.card_data.options,
        'correct_answer': body.card_data.correct_answer,
        'explanation': body.card_data.explanation,
        'media_urls': [],
        'created_at': now,
    }
    result = await cards_col.insert_one(card_doc)
    card_id = str(result.inserted_id)

    # Criar registro de review inicial (card está pronto para treino imediato)
    review_doc = {
        'card_id': card_id,
        'user_id': user_id,
        'next_review_date': now,
        'interval': 1,
        'ease_factor': 2.5,
        'repetitions': 0,
    }
    await reviews_col.insert_one(review_doc)

    # Dispara a geração de imagem da carta em background
    gemini_client = getattr(request.app.state, 'gemini_webapi_client', None)
    if (
        body.generate_image
        and gemini_client
        and body.card_data.visual_prompt_idea
    ):
        background_tasks.add_task(
            get_or_generate_card_image,
            card_id,
            body.card_data.visual_prompt_idea,
            gemini_client,
        )

    return SwipeResponse(
        success=True,
        message='Card salvo no seu deck de treinamento.',
        card_id=card_id,
    )


@router.get('/{domain_id}', response_model=list[ScenarioCard])
async def list_cards(
    domain_id: str,
    current_user=Depends(get_current_active_user),
    domains_col=Depends(get_domains_collection),
    cards_col=Depends(get_scenario_cards_collection),
):
    """Lista todos os cards salvos de um domínio."""
    user_id = str(current_user['_id'])

    try:
        oid = ObjectId(domain_id)
    except Exception:
        raise HTTPException(status_code=400, detail='ID de domínio inválido')

    domain = await domains_col.find_one({'_id': oid, 'user_id': user_id})
    if not domain:
        raise HTTPException(status_code=404, detail='Domínio não encontrado')

    docs = (
        await cards_col
        .find({'domain_id': domain_id, 'user_id': user_id})
        .sort('created_at', -1)
        .to_list(length=None)
    )

    cards = []
    for doc in docs:
        doc['_id'] = str(doc['_id'])
        cards.append(ScenarioCard(**doc))
    return cards


@router.delete('/{card_id}', response_model=DefautMessage)
async def delete_card(
    card_id: str,
    current_user=Depends(get_current_active_user),
    cards_col=Depends(get_scenario_cards_collection),
    reviews_col=Depends(get_reviews_collection),
):
    """Remove um card e seu registro de review."""
    user_id = str(current_user['_id'])

    try:
        oid = ObjectId(card_id)
    except Exception:
        raise HTTPException(status_code=400, detail='ID de card inválido')

    doc = await cards_col.find_one({'_id': oid, 'user_id': user_id})
    if not doc:
        raise HTTPException(status_code=404, detail='Card não encontrado')

    await reviews_col.delete_many({'card_id': card_id, 'user_id': user_id})
    await cards_col.delete_one({'_id': oid})

    return DefautMessage(success=True, message='Card removido.')


@router.put('/{card_id}', response_model=ScenarioCard)
async def update_card(
    card_id: str,
    body: ScenarioCardUpdate,
    current_user=Depends(get_current_active_user),
    cards_col=Depends(get_scenario_cards_collection),
):
    """Atualiza os campos de texto de um card guardado."""
    user_id = str(current_user['_id'])

    try:
        oid = ObjectId(card_id)
    except Exception:
        raise HTTPException(status_code=400, detail='ID de card inválido')

    doc = await cards_col.find_one({'_id': oid, 'user_id': user_id})
    if not doc:
        raise HTTPException(status_code=404, detail='Card não encontrado')

    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        doc['_id'] = str(doc['_id'])
        return ScenarioCard(**doc)

    await cards_col.update_one({'_id': oid}, {'$set': updates})
    doc.update(updates)
    doc['_id'] = str(doc['_id'])
    return ScenarioCard(**doc)


@router.post('/{card_id}/regenerate-image', response_model=DefautMessage)
async def regenerate_card_image(
    card_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_active_user),
    cards_col=Depends(get_scenario_cards_collection),
):
    """Regenera a imagem de um card via IA, ignorando o cache."""
    user_id = str(current_user['_id'])

    try:
        oid = ObjectId(card_id)
    except Exception:
        raise HTTPException(status_code=400, detail='ID de card inválido')

    doc = await cards_col.find_one({'_id': oid, 'user_id': user_id})
    if not doc:
        raise HTTPException(status_code=404, detail='Card não encontrado')

    gemini_client = getattr(request.app.state, 'gemini_webapi_client', None)
    if not gemini_client:
        raise HTTPException(
            status_code=503, detail='Motor de IA não está configurado.'
        )

    visual_prompt = doc.get('visual_prompt_idea') or doc.get(
        'scenario_context', ''
    )
    background_tasks.add_task(
        get_or_generate_card_image, card_id, visual_prompt, gemini_client, True
    )

    return DefautMessage(
        success=True, message='Regeneração de imagem iniciada em background.'
    )


@router.post('/{card_id}/improve-image', response_model=DefautMessage)
async def improve_card_image(  # noqa: PLR0913, PLR0917
    card_id: str,
    body: ImageImproveRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_active_user),
    cards_col=Depends(get_scenario_cards_collection),
):
    """Melhora a imagem do card com um prompt de estilo via IA."""
    user_id = str(current_user['_id'])

    try:
        oid = ObjectId(card_id)
    except Exception:
        raise HTTPException(status_code=400, detail='ID de card inválido')

    doc = await cards_col.find_one({'_id': oid, 'user_id': user_id})
    if not doc:
        raise HTTPException(status_code=404, detail='Card não encontrado')

    gemini_client = getattr(request.app.state, 'gemini_webapi_client', None)
    if not gemini_client:
        raise HTTPException(
            status_code=503, detail='Motor de IA não está configurado.'
        )

    base_prompt = doc.get('visual_prompt_idea') or doc.get(
        'scenario_context', ''
    )
    background_tasks.add_task(
        improve_image_with_ai,
        'cards',
        card_id,
        body.style_prompt,
        build_card_image_prompt(base_prompt),
        gemini_client,
    )

    return DefautMessage(
        success=True, message='Melhoria de imagem iniciada em background.'
    )


@router.post('/{card_id}/upload-image', response_model=DefautMessage)
async def upload_card_image(
    card_id: str,
    file: UploadFile = File(...),
    current_user=Depends(get_current_active_user),
    cards_col=Depends(get_scenario_cards_collection),
):
    """Faz upload manual de imagem para o card."""
    user_id = str(current_user['_id'])

    try:
        oid = ObjectId(card_id)
    except Exception:
        raise HTTPException(status_code=400, detail='ID de card inválido')

    doc = await cards_col.find_one({'_id': oid, 'user_id': user_id})
    if not doc:
        raise HTTPException(status_code=404, detail='Card não encontrado')

    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400, detail='O ficheiro deve ser uma imagem.'
        )

    cards_dir = os.path.join(MEDIA_DIR, 'cards')
    os.makedirs(cards_dir, exist_ok=True)
    dest_path = os.path.join(cards_dir, f'{card_id}.png')

    with open(dest_path, 'wb') as out:
        shutil.copyfileobj(file.file, out)

    abs_url = f'/media/cards/{card_id}.png'
    await cards_col.update_one(
        {'_id': oid}, {'$set': {'media_urls': [abs_url]}}
    )

    return DefautMessage(success=True, message='Imagem carregada com sucesso.')


@router.delete('/{card_id}/image', response_model=DefautMessage)
async def remove_card_image(
    card_id: str,
    current_user=Depends(get_current_active_user),
    cards_col=Depends(get_scenario_cards_collection),
):
    """Remove a imagem associada ao card."""
    user_id = str(current_user['_id'])

    try:
        oid = ObjectId(card_id)
    except Exception:
        raise HTTPException(status_code=400, detail='ID de card inválido')

    doc = await cards_col.find_one({'_id': oid, 'user_id': user_id})
    if not doc:
        raise HTTPException(status_code=404, detail='Card não encontrado')

    img_path = os.path.join(MEDIA_DIR, 'cards', f'{card_id}.png')
    if os.path.exists(img_path):
        os.remove(img_path)

    await cards_col.update_one({'_id': oid}, {'$set': {'media_urls': []}})

    return DefautMessage(success=True, message='Imagem removida.')
