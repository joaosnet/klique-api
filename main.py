import asyncio
import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from gemini_webapi import GeminiClient

# inicializa o logger antes de qualquer outra coisa
from src.logger import logger
from src.routers import generate, batch
from src.services.gemini import GeminiService
from src.services.firebase_service import FirebaseService
from src.services.drive_service import DriveService
from src.services.mongo_service import MongoService
from src.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicia os serviços e os armazena no estado da aplicação
    try:
        app.state.firebase_service = FirebaseService()
        app.state.drive_service = DriveService(settings.GOOGLE_APPLICATION_CREDENTIALS)
        app.state.mongo_service = MongoService()

        gemini_service = GeminiService()
        await gemini_service.client.init(
            timeout=settings.GEMINI_TIMEOUT,
            auto_close=settings.GEMINI_AUTO_CLOSE,
            close_delay=settings.GEMINI_CLOSE_DELAY,
        )
        app.state.gemini_service = gemini_service
        # app.state.chat_sessions = {} # Removido, não é mais necessário
        app.state.sem = asyncio.Semaphore(settings.GEMINI_CONCURRENCY_LIMIT)

        logger.info("Serviços inicializados com sucesso.")
    except Exception as e:
        logger.critical(f"Falha ao inicializar os serviços: {e}", exc_info=True)
        # Em um cenário real, você pode querer parar a aplicação se os serviços essenciais falharem
        raise
        
    yield
    
    # Limpeza (se necessário)
    logger.info("Encerrando a API.")

app = FastAPI(lifespan=lifespan)

app.include_router(generate.router)
app.include_router(batch.router)

logger.info("API iniciada. Acesse http://127.0.0.1:8000/docs")
