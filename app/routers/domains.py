"""
Rotas para gerenciamento de Domínios de Jogo (Decks).

Cada domínio representa uma área de treino preditivo do usuário,
como "Dinâmicas de Encontros", "Geopolítica" ou "Negociação Salarial".
"""

import asyncio
import os
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
from ..services.image_generation import (
    MEDIA_DIR,
    build_domain_image_prompt,
    get_or_generate_domain_image,
    improve_image_with_ai,
)
from .schemas import (
    DefautMessage,
    Domain,
    DomainCreate,
    DomainStats,
    DomainUpdate,
    DomainWithStats,
    ImageImproveRequest,
)

router = APIRouter(prefix='/api/domains', tags=['domains'])


async def _compute_domain_stats(domain_id: str, user_id: str) -> DomainStats:
    """Calcula as estatísticas de um domínio usando consultas concorrentes."""
    cards_col = get_scenario_cards_collection()
    reviews_col = get_reviews_collection()
    logs_col = get_simulation_logs_collection()

    now = datetime.now(timezone.utc)

    # 1. Obter contagem e IDs concorrentemente
    cards_count_t = cards_col.count_documents({
        'domain_id': domain_id,
        'user_id': user_id,
    })
    card_docs_t = cards_col.find(
        {'domain_id': domain_id, 'user_id': user_id},
        {'_id': 1},
    ).to_list(length=None)

    cards_count, card_docs = await asyncio.gather(cards_count_t, card_docs_t)

    card_ids = [str(doc['_id']) for doc in card_docs]

    due_today = 0
    accuracy = 0.0

    # 2. Se houver cards, obter logs e revisões pendentes concorrentemente
    if card_ids:

        async def fetch_due_today():
            return await reviews_col.count_documents({
                'card_id': {'$in': card_ids},
                'user_id': user_id,
                'next_review_date': {'$lte': now},
            })

        async def fetch_accuracy():
            pipeline = [
                {'$match': {'domain_id': domain_id, 'user_id': user_id}},
                {
                    '$group': {
                        '_id': None,
                        'avg': {'$avg': '$performance_rating'},
                    }
                },
            ]
            cursor = await logs_col.aggregate(pipeline)
            raw_avg = 0.0
            async for doc in cursor:
                raw_avg = doc.get('avg', 0.0)
                break
            return round(raw_avg / 5.0, 2)

        due_today, accuracy = await asyncio.gather(
            fetch_due_today(), fetch_accuracy()
        )

    # O nome do domínio será preenchido pelo caller
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

    # Preparar as instâncias do modelo de Domínio primariamente
    domain_objects = []
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
        domain_objects.append((domain_id, domain))

    # Computar estatísticas concorrentemente para eliminar o N+1 fallback block
    if domain_objects:
        stats_list = await asyncio.gather(*[
            _compute_domain_stats(d_id, user_id) for d_id, _ in domain_objects
        ])
    else:
        stats_list = []

    for (domain_id, domain), stats in zip(domain_objects, stats_list):
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
async def delete_domain(  # noqa: PLR0913, PLR0917
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


@router.put('/{domain_id}', response_model=Domain)
async def update_domain(
    domain_id: str,
    data: DomainUpdate,
    current_user=Depends(get_current_active_user),
    domains_col=Depends(get_domains_collection),
):
    """Atualiza nome e/ou tema de um domínio."""
    user_id = str(current_user['_id'])

    try:
        oid = ObjectId(domain_id)
    except Exception:
        raise HTTPException(status_code=400, detail='ID de domínio inválido')

    doc = await domains_col.find_one({'_id': oid, 'user_id': user_id})
    if not doc:
        raise HTTPException(status_code=404, detail='Domínio não encontrado')

    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    # If theme changed, clear image_url so it can be regenerated
    if 'theme' in updates and updates['theme'] != doc.get('theme'):
        updates['image_url'] = None

    if not updates:
        doc['_id'] = str(doc['_id'])
        return Domain(**doc)

    await domains_col.update_one({'_id': oid}, {'$set': updates})
    doc.update(updates)
    doc['_id'] = str(doc['_id'])
    return Domain(**doc)


@router.post('/{domain_id}/regenerate-image', response_model=DefautMessage)
async def regenerate_domain_image(
    domain_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_active_user),
    domains_col=Depends(get_domains_collection),
):
    """Regenera a imagem do domínio via IA, ignorando o cache."""
    user_id = str(current_user['_id'])

    try:
        oid = ObjectId(domain_id)
    except Exception:
        raise HTTPException(status_code=400, detail='ID de domínio inválido')

    doc = await domains_col.find_one({'_id': oid, 'user_id': user_id})
    if not doc:
        raise HTTPException(status_code=404, detail='Domínio não encontrado')

    gemini_client = getattr(request.app.state, 'gemini_webapi_client', None)
    if not gemini_client:
        raise HTTPException(
            status_code=503, detail='Motor de IA não está configurado.'
        )

    background_tasks.add_task(
        get_or_generate_domain_image, doc['theme'], gemini_client, True
    )

    return DefautMessage(
        success=True, message='Regeneração de imagem iniciada em background.'
    )


@router.post('/{domain_id}/improve-image', response_model=DefautMessage)
async def improve_domain_image(  # noqa: PLR0913, PLR0917
    domain_id: str,
    body: ImageImproveRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    current_user=Depends(get_current_active_user),
    domains_col=Depends(get_domains_collection),
):
    """Melhora a imagem do domínio com um prompt de estilo via IA."""
    user_id = str(current_user['_id'])

    try:
        oid = ObjectId(domain_id)
    except Exception:
        raise HTTPException(status_code=400, detail='ID de domínio inválido')

    doc = await domains_col.find_one({'_id': oid, 'user_id': user_id})
    if not doc:
        raise HTTPException(status_code=404, detail='Domínio não encontrado')

    gemini_client = getattr(request.app.state, 'gemini_webapi_client', None)
    if not gemini_client:
        raise HTTPException(
            status_code=503, detail='Motor de IA não está configurado.'
        )

    theme = doc['theme']
    base_prompt = build_domain_image_prompt(theme)
    # Use domain_id as filename so it doesn't conflict with the shared theme cache  # noqa: E501
    background_tasks.add_task(
        improve_image_with_ai,
        'domains',
        domain_id,
        body.style_prompt,
        base_prompt,
        gemini_client,
    )
    # Update the domain's image_url to point to the custom file
    abs_url = f'/media/domains/{domain_id}.png'
    await domains_col.update_one(
        {'_id': oid}, {'$set': {'image_url': abs_url}}
    )  # noqa: E501

    return DefautMessage(
        success=True, message='Melhoria de imagem iniciada em background.'
    )


@router.post('/{domain_id}/upload-image', response_model=DefautMessage)
async def upload_domain_image(
    domain_id: str,
    file: UploadFile = File(...),
    current_user=Depends(get_current_active_user),
    domains_col=Depends(get_domains_collection),
):
    """Faz upload manual de imagem para o domínio."""
    user_id = str(current_user['_id'])

    try:
        oid = ObjectId(domain_id)
    except Exception:
        raise HTTPException(status_code=400, detail='ID de domínio inválido')

    doc = await domains_col.find_one({'_id': oid, 'user_id': user_id})
    if not doc:
        raise HTTPException(status_code=404, detail='Domínio não encontrado')

    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400, detail='O ficheiro deve ser uma imagem.'
        )

    domains_dir = os.path.join(MEDIA_DIR, 'domains')
    os.makedirs(domains_dir, exist_ok=True)
    dest_path = os.path.join(domains_dir, f'{domain_id}.png')

    with open(dest_path, 'wb') as out:
        shutil.copyfileobj(file.file, out)

    abs_url = f'/media/domains/{domain_id}.png'
    await domains_col.update_one(
        {'_id': oid}, {'$set': {'image_url': abs_url}}
    )

    return DefautMessage(success=True, message='Imagem carregada com sucesso.')


@router.delete('/{domain_id}/image', response_model=DefautMessage)
async def remove_domain_image(
    domain_id: str,
    current_user=Depends(get_current_active_user),
    domains_col=Depends(get_domains_collection),
):
    """Remove a imagem personalizada do domínio."""
    user_id = str(current_user['_id'])

    try:
        oid = ObjectId(domain_id)
    except Exception:
        raise HTTPException(status_code=400, detail='ID de domínio inválido')

    doc = await domains_col.find_one({'_id': oid, 'user_id': user_id})
    if not doc:
        raise HTTPException(status_code=404, detail='Domínio não encontrado')

    # Remove the custom domain image file
    img_path = os.path.join(MEDIA_DIR, 'domains', f'{domain_id}.png')
    if os.path.exists(img_path):
        os.remove(img_path)

    await domains_col.update_one({'_id': oid}, {'$set': {'image_url': None}})

    return DefautMessage(success=True, message='Imagem removida.')
