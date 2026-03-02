import os
import warnings
from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
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
    models,
    oracle_analytics,
    payments,
    profile_router,
    register,
    srs,
)
from .scheduler import setup_scheduler, start_scheduler, stop_scheduler

warnings.filterwarnings(
    'ignore',
    category=UserWarning,
    message=r'.*Pydantic V1.*',
    module=r'langchain_core.*',
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de ciclo de vida do FastAPI para inicializar e
    encerrar os serviços da aplicação.
    """
    # Inicializa o cliente do banco de dados no startup
    app.state.db_client = get_client()

    # Inicializa o cliente Gemini API oficial (usando GOOGLE_API_KEY)
    gemini_client = None
    if SECURE_1PSID:
        try:
            logger.info('Inicializando cliente GeminiWeb API (MCP)')
            gemini_client = GeminiClient(SECURE_1PSID, SECURE_1PSIDTS)
            await gemini_client.init(timeout=30)
            app.state.gemini_webapi_client = gemini_client
            logger.success('Cliente GeminiWeb API inicializado com sucesso')
        except Exception as e:
            logger.warning(f'Falha ao inicializar GeminiWeb API: {e}')
            app.state.gemini_webapi_client = None
    else:
        logger.info(
            'SECURE_1PSID não configurado — Motor do Oráculo desabilitado'
        )
        app.state.gemini_webapi_client = None

    # Configura e inicia o scheduler de tarefas agendadas
    await setup_scheduler()
    await start_scheduler()

    # Inicializa o ProcessPoolExecutor para bypassar o GIL em tarefas pesadas
    app.state.process_pool = ProcessPoolExecutor()
    logger.info('ProcessPoolExecutor (Multiprocessing) global inicializado')

    yield

    # Encerra os serviços ao finalizar a aplicação
    app.state.process_pool.shutdown()
    await stop_scheduler()
    await close_db_connection()


app = FastAPI(title='OmniFlash API', version='1.0.0', lifespan=lifespan)


origins = [
    'https://omniflash.app',
    'http://omniflash.app',
    'https://fotodenatal.me',
    'http://fotodenatal.me',
    'https://localhost',
    'http://localhost',
    'http://localhost:8080',
    'http://localhost:8000',
    'http://localhost:3000',
    'http://localhost:5173',
    'capacitor://localhost',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Add GZipMiddleware for response compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware('http')
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers['Strict-Transport-Security'] = (
        'max-age=31536000; includeSubDomains'
    )
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


# Setup templates and static files

MEDIA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), 'generated_media'
)
os.makedirs(MEDIA_DIR, exist_ok=True)
os.makedirs(os.path.join(MEDIA_DIR, 'domains'), exist_ok=True)
os.makedirs(os.path.join(MEDIA_DIR, 'cards'), exist_ok=True)
os.makedirs(os.path.join(MEDIA_DIR, 'avatars'), exist_ok=True)

app.mount('/media', StaticFiles(directory=MEDIA_DIR), name='media')


# @app.get('/', response_class=HTMLResponse)
# async def serve_frontend(request: Request):
#     """Serve the main frontend page."""
#     return templates.TemplateResponse('index.html', {'request': request})


# Include routers
app.include_router(auth.router)
app.include_router(register.router)
app.include_router(credits.router)
app.include_router(payments.router)
app.include_router(domains.router)
app.include_router(cards.router)
app.include_router(srs.router)
app.include_router(oracle_analytics.router)
app.include_router(profile_router.router)
app.include_router(models.router)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
