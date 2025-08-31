import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from gemini_webapi import GeminiClient

from src.config import (
    GEMINI_1PSID,
    GEMINI_1PSIDTS,
    PROXY,
    TIMEOUT,
    AUTO_CLOSE,
    CLOSE_DELAY,
    CONCURRENCY_LIMIT,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = GeminiClient(GEMINI_1PSID or None, GEMINI_1PSIDTS or None, proxy=PROXY)
    await client.init(
        timeout=TIMEOUT,
        auto_close=AUTO_CLOSE,
        close_delay=CLOSE_DELAY,
        auto_refresh=True,  # mantém cookies atualizados
    )
    app.state.gemini = client
    app.state.sem = asyncio.Semaphore(CONCURRENCY_LIMIT)
    try:
        yield
    finally:
        # encerra conexões
        await client.close()