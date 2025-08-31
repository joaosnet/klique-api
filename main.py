from fastapi import FastAPI

# inicializa o logger antes de qualquer outra coisa
from src.logger import logger

from src.services.gemini import lifespan
from src.routers import generate, batch

app = FastAPI(lifespan=lifespan)

app.include_router(generate.router)
app.include_router(batch.router)

logger.info("API iniciada. Acesse http://127.0.0.1:8000/docs")
