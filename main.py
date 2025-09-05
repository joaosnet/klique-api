import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from gemini_webapi import GeminiClient

from src.config import SECURE_1PSID, SECURE_1PSIDTS
from src.database import close_mongo_connection, connect_to_mongo
from src.logger import logger
from src.routers import auth, batch, generate, register, whatsapp
from src.services.gemini_app import GeminiAppService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicia o cliente Gemini e o armazena no estado da aplicação
    connect_to_mongo()
    client = GeminiClient(
        # secure_1psid=SECURE_1PSID,
        # secure_1psidts=SECURE_1PSIDTS,
    )
    await client.init()
    app.state.gemini = client
    app.state.gemini_service = GeminiAppService()
    app.state.chat_sessions = {}
    app.state.sem = asyncio.Semaphore(5)  # Limita a 5 requisições concorrentes
    logger.info('Cliente Gemini e serviço inicializados.')
    yield
    # Limpeza (se necessário)
    close_mongo_connection()
    logger.info('Encerrando a API.')


app = FastAPI(lifespan=lifespan, title='Klique AI API', version='1.0.0')


origins = [
    'http://localhost.tiangolo.com',
    'https://localhost.tiangolo.com',
    'http://localhost',
    'http://localhost:8080',
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(generate.router)
app.include_router(batch.router)
app.include_router(auth.router)
app.include_router(register.router)
app.include_router(whatsapp.router)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
