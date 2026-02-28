"""
Motor de Repetição Espaçada Estratégico (SRS) — Algoritmo SuperMemo-2.

O SM-2 define que a qualidade da memória deve ser avaliada em escala 0-5:
- 5: Resposta perfeita
- 4: Hesitação leve mas correta
- 3: Correta com dificuldade significativa
- 2: Incorreta — a resposta correta parecia fácil de lembrar
- 1: Incorreta — a resposta correta foi lembrada
- 0: Completamente errada
"""

from datetime import datetime, timedelta, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from ..database import (
    get_reviews_collection,
    get_scenario_cards_collection,
    get_simulation_logs_collection,
)
from ..dependencies import get_current_active_user
from .schemas import (
    DueCard,
    Review,
    ReviewSubmitRequest,
    ReviewSubmitResponse,
    ScenarioCard,
    SRSStats,
)

router = APIRouter(prefix='/api/srs', tags=['srs'])


def _apply_sm2(
    interval: int, ease_factor: float, repetitions: int, quality: int
):
    """
    Aplica o algoritmo SuperMemo-2 e retorna (new_interval, new_ef, new_reps).
    """
    if quality >= 3:
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(interval * ease_factor)
        new_ef = (
            ease_factor + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        )
        new_ef = max(1.3, new_ef)
        new_reps = repetitions + 1
    else:
        new_interval = 1
        new_ef = ease_factor
        new_reps = 0

    return new_interval, new_ef, new_reps


@router.get('/due', response_model=list[DueCard])
async def get_due_cards(
    current_user=Depends(get_current_active_user),
    reviews_col=Depends(get_reviews_collection),
    cards_col=Depends(get_scenario_cards_collection),
):
    """Retorna os cards vencidos para revisão hoje, ordenados por data."""
    user_id = str(current_user['_id'])
    now = datetime.now(timezone.utc)

    due_reviews = (
        await reviews_col
        .find({
            'user_id': user_id,
            'next_review_date': {'$lte': now},
        })
        .sort('next_review_date', 1)
        .to_list(length=50)
    )

    result = []
    for review_doc in due_reviews:
        card_id = review_doc['card_id']
        try:
            card_oid = ObjectId(card_id)
        except Exception:
            continue

        card_doc = await cards_col.find_one({
            '_id': card_oid,
            'user_id': user_id,
        })
        if not card_doc:
            continue

        card_doc['_id'] = str(card_doc['_id'])
        review_doc['_id'] = str(review_doc['_id'])

        result.append(
            DueCard(
                card=ScenarioCard(**card_doc),
                review=Review(**review_doc),
            )
        )

    return result


@router.post('/review', response_model=ReviewSubmitResponse)
async def submit_review(
    body: ReviewSubmitRequest,
    current_user=Depends(get_current_active_user),
    reviews_col=Depends(get_reviews_collection),
    cards_col=Depends(get_scenario_cards_collection),
    logs_col=Depends(get_simulation_logs_collection),
):
    """
    Submete a avaliação de performance de um card (0-5) e
    atualiza o agendamento de revisão via SM-2.
    """
    user_id = str(current_user['_id'])

    try:
        card_oid = ObjectId(body.card_id)
    except Exception:
        raise HTTPException(status_code=400, detail='ID de card inválido')

    card_doc = await cards_col.find_one({'_id': card_oid, 'user_id': user_id})
    if not card_doc:
        raise HTTPException(status_code=404, detail='Card não encontrado')

    domain_id = card_doc.get('domain_id', '')

    review_doc = await reviews_col.find_one({
        'card_id': body.card_id,
        'user_id': user_id,
    })
    if not review_doc:
        # Criar registro se não existir (card sem review inicial)
        now = datetime.now(timezone.utc)
        review_doc = {
            'card_id': body.card_id,
            'user_id': user_id,
            'next_review_date': now,
            'interval': 1,
            'ease_factor': 2.5,
            'repetitions': 0,
        }
        await reviews_col.insert_one(review_doc)

    interval = review_doc.get('interval', 1)
    ease_factor = review_doc.get('ease_factor', 2.5)
    repetitions = review_doc.get('repetitions', 0)

    new_interval, new_ef, new_reps = _apply_sm2(
        interval, ease_factor, repetitions, body.performance_rating
    )

    now = datetime.now(timezone.utc)
    next_review = now + timedelta(days=new_interval)

    await reviews_col.update_one(
        {'card_id': body.card_id, 'user_id': user_id},
        {
            '$set': {
                'interval': new_interval,
                'ease_factor': new_ef,
                'repetitions': new_reps,
                'next_review_date': next_review,
            }
        },
    )

    log_doc = {
        'user_id': user_id,
        'card_id': body.card_id,
        'domain_id': domain_id,
        'performance_rating': body.performance_rating,
        'reviewed_at': now,
    }
    await logs_col.insert_one(log_doc)

    return ReviewSubmitResponse(
        success=True,
        next_review_date=next_review,
        interval_days=new_interval,
        new_ease_factor=round(new_ef, 3),
    )


@router.get('/stats', response_model=SRSStats)
async def get_srs_stats(
    current_user=Depends(get_current_active_user),
    reviews_col=Depends(get_reviews_collection),
    logs_col=Depends(get_simulation_logs_collection),
):
    """Retorna estatísticas gerais de treinamento do usuário."""
    user_id = str(current_user['_id'])
    now = datetime.now(timezone.utc)

    total_trained = await logs_col.count_documents({'user_id': user_id})

    due_today = await reviews_col.count_documents({
        'user_id': user_id,
        'next_review_date': {'$lte': now},
    })

    # Cards "dominados": ease_factor >= 2.5 e interval >= 21 dias
    cards_mastered = await reviews_col.count_documents({
        'user_id': user_id,
        'ease_factor': {'$gte': 2.5},
        'interval': {'$gte': 21},
    })

    # Calcular streak: dias consecutivos com pelo menos 1 revisão
    streak_days = await _calculate_streak(user_id, logs_col)

    return SRSStats(
        total_trained=total_trained,
        streak_days=streak_days,
        cards_mastered=cards_mastered,
        due_today=due_today,
    )


async def _calculate_streak(user_id: str, logs_col) -> int:
    """Conta dias consecutivos de treino até hoje."""
    pipeline = [
        {'$match': {'user_id': user_id}},
        {
            '$project': {
                'day': {
                    '$dateToString': {
                        'format': '%Y-%m-%d',
                        'date': '$reviewed_at',
                    }
                }
            }
        },
        {'$group': {'_id': '$day'}},
        {'$sort': {'_id': -1}},
    ]
    cursor = await logs_col.aggregate(pipeline)
    days_docs = []
    async for doc in cursor:
        days_docs.append(doc)
    if not days_docs:
        return 0

    today = datetime.now(timezone.utc).date()
    streak = 0

    for i, doc in enumerate(days_docs):
        day = datetime.strptime(doc['_id'], '%Y-%m-%d').date()
        expected = today - timedelta(days=i)
        if day == expected:
            streak += 1
        else:
            break

    return streak
