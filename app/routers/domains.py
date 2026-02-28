"""
Rotas para gerenciamento de Domínios de Jogo (Decks).

Cada domínio representa uma área de treino preditivo do usuário,
como "Dinâmicas de Encontros", "Geopolítica" ou "Negociação Salarial".
"""

from datetime import datetime, timezone

from bson import ObjectId
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
    status,
)

from ..database import (
    get_domain_images_collection,
    get_domains_collection,
    get_reviews_collection,
    get_scenario_cards_collection,
    get_simulation_logs_collection,
)
from ..dependencies import get_current_active_user
from ..services.image_generation import get_or_generate_domain_image
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
        cursor = await logs_col.aggregate(pipeline)
        result = []
        async for doc in cursor:
            result.append(doc)
            if len(result) >= 1:
                break
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
    request: Request,
    data: DomainCreate,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_active_user),
    domains_col=Depends(get_domains_collection),
):
    """Cria um novo domínio de treino para o usuário autenticado."""
    doc = {
        'user_id': str(current_user['_id']),
        'name': data.name.strip(),
        'theme': data.theme.strip(),
        'image_url': None,
        'created_at': datetime.now(timezone.utc),
    }
    result = await domains_col.insert_one(doc)
    doc['_id'] = str(result.inserted_id)

    # Dispara a geração de imagem em background
    gemini_client = getattr(request.app.state, 'gemini_webapi_client', None)
    if gemini_client:
        background_tasks.add_task(
            get_or_generate_domain_image, doc['theme'], gemini_client
        )

    return Domain(**doc)


@router.get('/', response_model=list[DomainWithStats])
async def list_domains(
    request: Request,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_active_user),
    domains_col=Depends(get_domains_collection),
):
    """Lista todos os domínios do usuário com suas estatísticas."""
    user_id = str(current_user['_id'])
    docs = (
        await domains_col
        .find({'user_id': user_id})
        .sort('created_at', -1)
        .to_list(length=None)
    )

    result = []
    img_col = get_domain_images_collection()
    for doc in docs:
        domain_id = str(doc['_id'])
        doc['_id'] = domain_id

        # Retrocompat: fill image_url from shared cache if missing in doc
        if not doc.get('image_url'):
            cached = await img_col.find_one({'theme': doc.get('theme', '')})
            if cached and cached.get('image_url'):
                doc['image_url'] = cached['image_url']
                # Persist it back so future reads are instant
                await domains_col.update_one(
                    {'_id': ObjectId(domain_id)},
                    {'$set': {'image_url': cached['image_url']}},
                )

        # Trigger generation if still no image
        if not doc.get('image_url'):
            gemini_client = getattr(
                request.app.state, 'gemini_webapi_client', None
            )
            if gemini_client:
                background_tasks.add_task(
                    get_or_generate_domain_image, doc['theme'], gemini_client
                )

        domain = Domain(**doc)
        stats = await _compute_domain_stats(domain_id, user_id)
        stats.domain_name = domain.name
        # Copiar a imagem para o domínio
        result.append(
            DomainWithStats(
                domain=domain, stats=stats, image_url=domain.image_url
            )
        )

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

    # Retrocompat: populate image_url from shared cache if domain doc lacks it
    if not doc.get('image_url'):
        img_col = get_domain_images_collection()
        cached = await img_col.find_one({'theme': doc.get('theme', '')})
        if cached and cached.get('image_url'):
            doc['image_url'] = cached['image_url']
            # Persist it back
            await domains_col.update_one(
                {'_id': oid},
                {'$set': {'image_url': cached['image_url']}},
            )

    domain = Domain(**doc)
    stats = await _compute_domain_stats(domain_id, user_id)
    stats.domain_name = domain.name
    return DomainWithStats(
        domain=domain, stats=stats, image_url=domain.image_url
    )


@router.delete('/{domain_id}', response_model=DefautMessage)
async def delete_domain(  # noqa: PLR0913
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
        await reviews_col.delete_many({
            'card_id': {'$in': card_ids},
            'user_id': user_id,
        })
        await logs_col.delete_many({
            'card_id': {'$in': card_ids},
            'user_id': user_id,
        })

    await cards_col.delete_many({'domain_id': domain_id, 'user_id': user_id})
    await domains_col.delete_one({'_id': oid})

    return DefautMessage(
        success=True, message='Domínio e todos os seus dados foram removidos.'
    )
