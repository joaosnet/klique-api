"""
Rotas para gerenciamento de Domínios de Jogo (Decks).

Cada domínio representa uma área de treino preditivo do usuário,
como "Dinâmicas de Encontros", "Geopolítica" ou "Negociação Salarial".
"""

from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from ..database import (
    get_domains_collection,
    get_reviews_collection,
    get_scenario_cards_collection,
    get_simulation_logs_collection,
)
from ..dependencies import get_current_active_user
from .schemas import (
    DefautMessage,
    Domain,
    DomainCreate,
    DomainStats,
    DomainWithStats,
)

router = APIRouter(prefix='/api/domains', tags=['domains'])


async def _compute_domain_stats(domain_id: str, user_id: str) -> DomainStats:
    """Calcula as estatísticas de um domínio."""
    cards_col = get_scenario_cards_collection()
    reviews_col = get_reviews_collection()
    logs_col = get_simulation_logs_collection()

    cards_count = await cards_col.count_documents({
        'domain_id': domain_id,
        'user_id': user_id,
    })

    now = datetime.now(timezone.utc)
    # Buscar IDs dos cards do domínio para cruzar com reviews
    card_docs = await cards_col.find(
        {'domain_id': domain_id, 'user_id': user_id},
        {'_id': 1},
    ).to_list(length=None)
    card_ids = [str(doc['_id']) for doc in card_docs]

    due_today = 0
    if card_ids:
        due_today = await reviews_col.count_documents({
            'card_id': {'$in': card_ids},
            'user_id': user_id,
            'next_review_date': {'$lte': now},
        })

    # Calcular precisão média dos logs
    accuracy = 0.0
    if card_ids:
        pipeline = [
            {'$match': {'domain_id': domain_id, 'user_id': user_id}},
            {'$group': {'_id': None, 'avg': {'$avg': '$performance_rating'}}},
        ]
        result = await logs_col.aggregate(pipeline).to_list(length=1)
        if result:
            raw_avg = result[0].get('avg', 0.0)
            accuracy = round(raw_avg / 5.0, 2)

    # Precisamos do nome — será preenchido pelo caller
    return DomainStats(
        domain_id=domain_id,
        domain_name='',
        cards_count=cards_count,
        due_today=due_today,
        accuracy=accuracy,
    )


@router.post('/', response_model=Domain, status_code=status.HTTP_201_CREATED)
async def create_domain(
    data: DomainCreate,
    current_user=Depends(get_current_active_user),
    domains_col=Depends(get_domains_collection),
):
    """Cria um novo domínio de treino para o usuário autenticado."""
    doc = {
        'user_id': str(current_user['_id']),
        'name': data.name.strip(),
        'theme': data.theme.strip(),
        'created_at': datetime.now(timezone.utc),
    }
    result = await domains_col.insert_one(doc)
    doc['_id'] = str(result.inserted_id)
    return Domain(**doc)


@router.get('/', response_model=list[DomainWithStats])
async def list_domains(
    current_user=Depends(get_current_active_user),
    domains_col=Depends(get_domains_collection),
):
    """Lista todos os domínios do usuário com suas estatísticas."""
    user_id = str(current_user['_id'])
    docs = await domains_col.find({'user_id': user_id}).sort('created_at', -1).to_list(length=None)

    result = []
    for doc in docs:
        domain_id = str(doc['_id'])
        doc['_id'] = domain_id
        domain = Domain(**doc)
        stats = await _compute_domain_stats(domain_id, user_id)
        stats.domain_name = domain.name
        result.append(DomainWithStats(domain=domain, stats=stats))

    return result


@router.get('/{domain_id}', response_model=DomainWithStats)
async def get_domain(
    domain_id: str,
    current_user=Depends(get_current_active_user),
    domains_col=Depends(get_domains_collection),
):
    """Retorna um domínio específico com suas estatísticas."""
    user_id = str(current_user['_id'])

    try:
        oid = ObjectId(domain_id)
    except Exception:
        raise HTTPException(status_code=400, detail='ID de domínio inválido')

    doc = await domains_col.find_one({'_id': oid, 'user_id': user_id})
    if not doc:
        raise HTTPException(status_code=404, detail='Domínio não encontrado')

    doc['_id'] = str(doc['_id'])
    domain = Domain(**doc)
    stats = await _compute_domain_stats(domain_id, user_id)
    stats.domain_name = domain.name
    return DomainWithStats(domain=domain, stats=stats)


@router.delete('/{domain_id}', response_model=DefautMessage)
async def delete_domain(
    domain_id: str,
    current_user=Depends(get_current_active_user),
    domains_col=Depends(get_domains_collection),
    cards_col=Depends(get_scenario_cards_collection),
    reviews_col=Depends(get_reviews_collection),
    logs_col=Depends(get_simulation_logs_collection),
):
    """Remove um domínio e todos os seus cards, reviews e logs."""
    user_id = str(current_user['_id'])

    try:
        oid = ObjectId(domain_id)
    except Exception:
        raise HTTPException(status_code=400, detail='ID de domínio inválido')

    doc = await domains_col.find_one({'_id': oid, 'user_id': user_id})
    if not doc:
        raise HTTPException(status_code=404, detail='Domínio não encontrado')

    # Buscar IDs dos cards para limpar reviews e logs
    card_docs = await cards_col.find(
        {'domain_id': domain_id, 'user_id': user_id}, {'_id': 1}
    ).to_list(length=None)
    card_ids = [str(c['_id']) for c in card_docs]

    if card_ids:
        await reviews_col.delete_many({'card_id': {'$in': card_ids}, 'user_id': user_id})
        await logs_col.delete_many({'card_id': {'$in': card_ids}, 'user_id': user_id})

    await cards_col.delete_many({'domain_id': domain_id, 'user_id': user_id})
    await domains_col.delete_one({'_id': oid})

    return DefautMessage(success=True, message='Domínio e todos os seus dados foram removidos.')
