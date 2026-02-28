"""
Rotas para geração e gerenciamento de Scenario Cards.

O endpoint principal (/generate-stream) usa Server-Sent Events (SSE)
para gerar um card por vez via Gemini WebAPI, replicando o padrão
do christmas.py.
"""

import json
import os
import re
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from ..database import (
    get_domains_collection,
    get_reviews_collection,
    get_scenario_cards_collection,
)
from ..dependencies import get_current_active_user
from .schemas import (
    DefautMessage,
    GenerateCardRequest,
    ScenarioCard,
    SwipeAction,
    SwipeResponse,
)

router = APIRouter(prefix='/api/cards', tags=['cards'])

# Caminho para o system prompt do Oracle
_ORACLE_PROMPT_PATH = os.path.join(
    os.path.dirname(__file__), '..', 'agents', 'omniflash_oracle_prompt.md'
)


def _load_oracle_prompt() -> str:
    with open(_ORACLE_PROMPT_PATH, 'r', encoding='utf-8') as f:
        return f.read()


async def generate_sse_event(event: str, data: dict) -> str:
    return f'event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n'


async def _card_generation_stream(
    domain_name: str,
    domain_theme: str,
    context: str | None,
    gemini_client,
):
    """Async generator que produz eventos SSE para geração de um card."""
    try:
        yield await generate_sse_event(
            'progress',
            {'step': 1, 'total': 3, 'message': 'Consultando o Oráculo...', 'percent': 20},
        )

        oracle_prompt = _load_oracle_prompt()
        user_message = (
            f'Domínio: {domain_name}\nTema: {domain_theme}\n'
        )
        if context:
            user_message += f'Contexto adicional: {context}\n'

        full_prompt = f'{oracle_prompt}\n\n---\n\n{user_message}'

        yield await generate_sse_event(
            'progress',
            {'step': 2, 'total': 3, 'message': 'Gerando cenário tático...', 'percent': 60},
        )

        response = await gemini_client.generate_content(full_prompt)
        raw_text = response.text.strip()

        # Extrair JSON — remover blocos de código markdown se presentes
        json_match = re.search(r'\{[\s\S]*\}', raw_text)
        if not json_match:
            yield await generate_sse_event(
                'error',
                {'message': 'Gemini não retornou JSON válido. Tente novamente.'},
            )
            return

        card_dict = json.loads(json_match.group(0))

        yield await generate_sse_event(
            'progress',
            {'step': 3, 'total': 3, 'message': 'Cenário pronto.', 'percent': 100},
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
            detail='Gemini WebAPI não está configurado. Verifique SECURE_1PSID no .env.',
        )

    async def stream_generator():
        async for chunk in _card_generation_stream(
            domain_name=domain['name'],
            domain_theme=domain['theme'],
            context=body.context,
            gemini_client=gemini_client,
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
async def swipe_card(
    body: SwipeAction,
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
        raise HTTPException(status_code=400, detail="action deve ser 'save' ou 'discard'")

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
        'template_type': body.card_data.template_type,
        'scenario_context': body.card_data.scenario_context,
        'question': body.card_data.question,
        'predicted_outcome': body.card_data.predicted_outcome,
        'game_theory_explanation': body.card_data.game_theory_explanation,
        'probability_heat_score': body.card_data.probability_heat_score,
        'visual_prompt_idea': body.card_data.visual_prompt_idea,
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

    docs = await cards_col.find(
        {'domain_id': domain_id, 'user_id': user_id}
    ).sort('created_at', -1).to_list(length=None)

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
