import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from gemini_webapi import GeminiClient
from fastapi.middleware.cors import CORSMiddleware
from src.logger import logger
from src.routers import generate, batch, auth
from src.services.gemini import GeminiService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicia o cliente Gemini e o armazena no estado da aplicação
    client = GeminiClient()
    await client.init()
    app.state.gemini = client
    app.state.gemini_service = GeminiService()
    app.state.chat_sessions = {}
    app.state.sem = asyncio.Semaphore(5)  # Limita a 5 requisições concorrentes
    logger.info("Cliente Gemini e serviço inicializados.")
    yield
    # Limpeza (se necessário)
    logger.info("Encerrando a API.")



app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(generate.router)
app.include_router(batch.router)
app.include_router(auth.router)

logger.info("API iniciada. Acesse http://127.0.0.1:8000/docs")
