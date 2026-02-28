"""
Rotas de Analytics do Estrategista (Dashboard do Oráculo).

Fornece dados agregados para o Dashboard: visão geral, radar de
proficiência por domínio e histórico de atividade dos últimos 7 dias.
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends

from ..database import (
    get_domains_collection,
    get_reviews_collection,
    get_scenario_cards_collection,
    get_simulation_logs_collection,
)
from ..dependencies import get_current_active_user
from .schemas import ActivityEntry, DashboardOverview, RadarEntry

router = APIRouter(prefix='/api/oracle', tags=['oracle'])


@router.get('/dashboard', response_model=DashboardOverview)
async def get_dashboard(
    current_user=Depends(get_current_active_user),
    domains_col=Depends(get_domains_collection),
    cards_col=Depends(get_scenario_cards_collection),
    reviews_col=Depends(get_reviews_collection),
    logs_col=Depends(get_simulation_logs_collection),
):
    """Retorna métricas de visão geral do estrategista."""
    user_id = str(current_user['_id'])
    now = datetime.now(timezone.utc)

    total_domains = await domains_col.count_documents({'user_id': user_id})
    total_cards = await cards_col.count_documents({'user_id': user_id})

    due_today = await reviews_col.count_documents({
        'user_id': user_id,
        'next_review_date': {'$lte': now},
    })

    week_ago = now - timedelta(days=7)
    weekly_trained = await logs_col.count_documents({
        'user_id': user_id,
        'reviewed_at': {'$gte': week_ago},
    })

    # Streak rápido (dias consecutivos)
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
    today = now.date()
    streak_days = 0
    for i, doc in enumerate(days_docs):
        day = datetime.strptime(doc['_id'], '%Y-%m-%d').date()
        if day == today - timedelta(days=i):
            streak_days += 1
        else:
            break

    return DashboardOverview(
        total_domains=total_domains,
        total_cards=total_cards,
        due_today=due_today,
        weekly_trained=weekly_trained,
        streak_days=streak_days,
    )


@router.get('/radar', response_model=list[RadarEntry])
async def get_radar(
    current_user=Depends(get_current_active_user),
    domains_col=Depends(get_domains_collection),
    logs_col=Depends(get_simulation_logs_collection),
):
    """
    Retorna proficiência por domínio para o gráfico radar.
    Accuracy = média de performance_rating / 5.
    """
    user_id = str(current_user['_id'])

    domains_docs = await domains_col.find({'user_id': user_id}).to_list(
        length=None
    )
    result = []

    for domain in domains_docs:
        domain_id = str(domain['_id'])
        pipeline = [
            {'$match': {'user_id': user_id, 'domain_id': domain_id}},
            {
                '$group': {
                    '_id': None,
                    'avg_rating': {'$avg': '$performance_rating'},
                    'count': {'$sum': 1},
                }
            },
        ]
        cursor = await logs_col.aggregate(pipeline)
        agg = []
        async for doc in cursor:
            agg.append(doc)
            if len(agg) >= 1:
                break
        if agg:
            avg = agg[0].get('avg_rating', 0.0)
            count = agg[0].get('count', 0)
            accuracy = round(avg / 5.0, 2)
        else:
            accuracy = 0.0
            count = 0

        result.append(
            RadarEntry(
                domain_id=domain_id,
                domain_name=domain['name'],
                accuracy=accuracy,
                trained_count=count,
            )
        )

    return result


@router.get('/activity', response_model=list[ActivityEntry])
async def get_activity(
    current_user=Depends(get_current_active_user),
    logs_col=Depends(get_simulation_logs_collection),
):
    """Retorna atividade de treino nos últimos 7 dias."""
    user_id = str(current_user['_id'])
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=6)

    pipeline = [
        {
            '$match': {
                'user_id': user_id,
                'reviewed_at': {'$gte': week_ago},
            }
        },
        {
            '$project': {
                'day': {
                    '$dateToString': {
                        'format': '%Y-%m-%d',
                        'date': '$reviewed_at',
                    }
                },
                'performance_rating': 1,
            }
        },
        {
            '$group': {
                '_id': '$day',
                'count': {'$sum': 1},
                'avg_rating': {'$avg': '$performance_rating'},
            }
        },
        {'$sort': {'_id': 1}},
    ]
    cursor = await logs_col.aggregate(pipeline)
    docs = []
    async for doc in cursor:
        docs.append(doc)

    # Preencher dias sem atividade com zeros
    activity_map = {
        doc['_id']: ActivityEntry(
            date=doc['_id'],
            count=doc['count'],
            avg_rating=round(doc.get('avg_rating', 0.0), 2),
        )
        for doc in docs
    }

    result = []
    for i in range(7):
        day = now.date() - timedelta(days=6 - i)
        day_str = day.strftime('%Y-%m-%d')
        result.append(
            activity_map.get(
                day_str, ActivityEntry(date=day_str, count=0, avg_rating=0.0)
            )
        )

    return result
