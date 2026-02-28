import warnings

warnings.filterwarnings(
    'ignore',
    category=UserWarning,
    message=r'.*Pydantic V1.*',
    module=r'langchain_core.*',
)

import os  # noqa: E402
from contextlib import asynccontextmanager  # noqa: E402

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from gemini_webapi import GeminiClient

from .config import SECURE_1PSID, SECURE_1PSIDTS
from .database import close_db_connection, get_client
from .logger import logger
from .routers import (
    auth,
    cards,
    credits,
    domains,
    oracle_analytics,
    payments,
    register,
    srs,
    whatsapp,
)
from .scheduler import setup_scheduler, start_scheduler, stop_scheduler
from .services.whatsapp import WhatsAppService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de ciclo de vida do FastAPI para inicializar e
    encerrar os serviços da aplicação.
    """
    # Inicializa o cliente do banco de dados no startup
    app.state.db_client = get_client()

    # Inicializa o serviço do WhatsApp
    whatsapp_service = WhatsAppService()
    app.state.whatsapp_service = whatsapp_service

    # Inicializa o cliente Gemini WebAPI (singleton)
    gemini_client = None
    if SECURE_1PSID:
        try:
            gemini_client = GeminiClient(SECURE_1PSID, SECURE_1PSIDTS or '')
            await gemini_client.init(
                timeout=60, auto_close=False, auto_refresh=True
            )
            app.state.gemini_webapi_client = gemini_client
            logger.success('Cliente Gemini WebAPI inicializado com sucesso')

            import asyncio  # noqa: PLC0415

            from .services.image_generation import init_demo_images
            asyncio.create_task(init_demo_images(gemini_client))
        except Exception as e:
            logger.warning(f'Falha ao inicializar Gemini WebAPI: {e}')
            app.state.gemini_webapi_client = None
    else:
        logger.warning(
            'SECURE_1PSID não configurado — Motor do Oráculo desabilitado'
        )
        app.state.gemini_webapi_client = None

    # Configura e inicia o scheduler de tarefas agendadas
    await setup_scheduler()
    await start_scheduler()

    yield

    # Encerra os serviços ao finalizar a aplicação
    await stop_scheduler()
    await whatsapp_service.close()
    if gemini_client:
        await gemini_client.close()
    await close_db_connection()


app = FastAPI(title='OmniFlash API', version='1.0.0', lifespan=lifespan)


origins = [
    'https://omniflash.app',
    'http://omniflash.app',
    'http://localhost',
    'http://localhost:8080',
    'http://localhost:8000',
    'http://localhost:3000',
    'http://localhost:5173',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Setup templates and static files

MEDIA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'generated_media'
)
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(os.path.join(MEDIA_DIR, 'domains'), exist_ok=True)
os.makedirs(os.path.join(MEDIA_DIR, 'cards'), exist_ok=True)

app.mount('/media', StaticFiles(directory=MEDIA_DIR), name='media')


# @app.get('/', response_class=HTMLResponse)
# async def serve_frontend(request: Request):
#     """Serve the main frontend page."""
#     return templates.TemplateResponse('index.html', {'request': request})


# Include routers
app.include_router(auth.router)
app.include_router(register.router)
app.include_router(whatsapp.router)
app.include_router(credits.router)
app.include_router(payments.router)
app.include_router(domains.router)
app.include_router(cards.router)
app.include_router(srs.router)
app.include_router(oracle_analytics.router)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
