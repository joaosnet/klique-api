"""
Router para analytics de links compartilhados.
Rastreia visualizações de preview (Open Graph) e cliques em links.
"""

import hashlib
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import FileResponse, JSONResponse

from app.database import get_link_analytics_collection
from app.logger import logger

router = APIRouter(prefix='/api/analytics', tags=['analytics'])

# Path para a imagem OG (dentro do app/static)
OG_IMAGE_PATH = Path(__file__).parent.parent / 'static' / 'og-preview.jpg'


def _hash_ip(ip: str) -> str:
    """Hash o IP para anonimização."""
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


def _get_client_ip(request: Request) -> str:
    """Extrai o IP real do cliente, considerando proxies."""
    # Verifica headers de proxy
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        # Pega o primeiro IP da lista (cliente original)
        return forwarded_for.split(',')[0].strip()

    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip

    return request.client.host if request.client else 'unknown'


def _detect_platform(user_agent: str) -> str:
    """Detecta a plataforma/app baseado no user-agent."""
    ua_lower = user_agent.lower()

    if 'whatsapp' in ua_lower:
        return 'whatsapp'
    elif 'facebookexternalhit' in ua_lower or 'facebot' in ua_lower:
        return 'facebook'
    elif 'telegrambot' in ua_lower:
        return 'telegram'
    elif 'twitterbot' in ua_lower:
        return 'twitter'
    elif 'linkedinbot' in ua_lower:
        return 'linkedin'
    elif 'slackbot' in ua_lower:
        return 'slack'
    elif 'discordbot' in ua_lower:
        return 'discord'
    else:
        return 'other'


@router.get('/og-image')
async def serve_og_image(request: Request):
    """
    Serve a imagem Open Graph e registra a visualização.
    Quando o WhatsApp/Facebook busca o preview, este endpoint é chamado.
    """
    try:
        # Coleta informações do request
        client_ip = _get_client_ip(request)
        user_agent = request.headers.get('User-Agent', 'unknown')
        platform = _detect_platform(user_agent)

        # Registra a view no MongoDB
        collection = get_link_analytics_collection()
        await collection.insert_one({
            'type': 'view',
            'ip_hash': _hash_ip(client_ip),
            'platform': platform,
            'user_agent': user_agent[:500],  # Limita tamanho
            'timestamp': datetime.now(timezone.utc),
            'referer': request.headers.get('Referer', ''),
        })

        logger.info(
            f'OG image view recorded from {platform} (IP hash: {_hash_ip(client_ip)[:8]}...)'
        )

    except Exception as e:
        # Não falha se analytics falhar - apenas log
        logger.warning(f'Failed to record OG view: {e}')

    # Retorna a imagem independente de sucesso no analytics
    if OG_IMAGE_PATH.exists():
        return FileResponse(
            OG_IMAGE_PATH,
            media_type='image/jpeg',
            headers={
                'Cache-Control': 'public, max-age=3600',  # Cache por 1 hora
            },
        )
    else:
        # Fallback: retorna 404 se imagem não existir
        return JSONResponse(
            status_code=404, content={'error': 'OG image not found'}
        )


@router.post('/click')
async def record_click(request: Request):
    """
    Registra um clique quando alguém acessa o site.
    Chamado pelo frontend no carregamento da página.
    """
    try:
        # Tenta pegar dados do body
        body = {}
        try:
            body = await request.json()
        except Exception:
            pass

        client_ip = _get_client_ip(request)
        user_agent = request.headers.get('User-Agent', 'unknown')

        # Registra o clique
        collection = get_link_analytics_collection()
        await collection.insert_one({
            'type': 'click',
            'ip_hash': _hash_ip(client_ip),
            'user_agent': user_agent[:500],
            'referrer': body.get(
                'referrer', request.headers.get('Referer', '')
            ),
            'timestamp': datetime.now(timezone.utc),
            'page': body.get('page', '/'),
        })

        logger.info(f'Click recorded (IP hash: {_hash_ip(client_ip)[:8]}...)')

        return JSONResponse(content={'status': 'ok'})

    except Exception as e:
        logger.warning(f'Failed to record click: {e}')
        # Retorna sucesso mesmo se falhar - não afeta UX
        return JSONResponse(content={'status': 'ok'})


@router.get('/stats')
async def get_stats():
    """
    Retorna estatísticas básicas de analytics.
    TODO: Adicionar autenticação admin.
    """
    try:
        collection = get_link_analytics_collection()

        # Conta views e cliques
        total_views = await collection.count_documents({'type': 'view'})
        total_clicks = await collection.count_documents({'type': 'click'})

        # Views por plataforma
        pipeline = [
            {'$match': {'type': 'view'}},
            {'$group': {'_id': '$platform', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}},
        ]
        views_by_platform = {}
        async for doc in collection.aggregate(pipeline):
            views_by_platform[doc['_id']] = doc['count']

        return JSONResponse(
            content={
                'total_views': total_views,
                'total_clicks': total_clicks,
                'conversion_rate': round(
                    (total_clicks / total_views * 100)
                    if total_views > 0
                    else 0,
                    2,
                ),
                'views_by_platform': views_by_platform,
            }
        )

    except Exception as e:
        logger.error(f'Failed to get analytics stats: {e}')
        return JSONResponse(
            status_code=500, content={'error': 'Failed to get stats'}
        )
