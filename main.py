import os
import asyncio
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from gemini_webapi import GeminiClient
from gemini_webapi.constants import Model
from gemini_webapi.exceptions import (
    TimeoutError,
    UsageLimitExceeded,
    ModelInvalid,
    TemporarilyBlocked,
    APIError,
)

GEMINI_1PSID = os.getenv("GEMINI_1PSID", "")
GEMINI_1PSIDTS = os.getenv("GEMINI_1PSIDTS", "")
PROXY = os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")
TIMEOUT = float(os.getenv("GEMINI_TIMEOUT", "30"))
AUTO_CLOSE = os.getenv("GEMINI_AUTO_CLOSE", "false").lower() == "true"
CLOSE_DELAY = float(os.getenv("GEMINI_CLOSE_DELAY", "300"))
CONCURRENCY_LIMIT = int(os.getenv("GEMINI_CONCURRENCY", "4"))  # ajuste conforme sua conta/infra

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

app = FastAPI(lifespan=lifespan)

class GenerateIn(BaseModel):
    prompt: str
    model: Optional[str] = None          # ex: "gemini-2.5-flash" | "gemini-2.5-pro" | "unspecified"
    gem: Optional[str] = None            # id de gem opcional
    files: Optional[List[str]] = None    # caminhos para arquivos opcionais
    chat_metadata: Optional[dict] = None # para continuar conversa (opcional)

@app.post("/generate")
async def generate(req: GenerateIn, request: Request):
    client: GeminiClient = request.app.state.gemini
    sem: asyncio.Semaphore = request.app.state.sem

    chat = None
    if req.chat_metadata:
        chat = client.start_chat(metadata=req.chat_metadata)

    async with sem:
        try:
            output = await client.generate_content(
                prompt=req.prompt,
                files=req.files,
                model=req.model or Model.UNSPECIFIED,
                gem=req.gem,
                chat=chat,
            )
        except UsageLimitExceeded as e:
            raise HTTPException(status_code=429, detail=str(e))
        except TimeoutError as e:
            raise HTTPException(status_code=504, detail=str(e))
        except ModelInvalid as e:
            raise HTTPException(status_code=400, detail=str(e))
        except TemporarilyBlocked as e:
            raise HTTPException(status_code=403, detail=str(e))
        except APIError as e:
            raise HTTPException(status_code=502, detail=str(e))

    return {
        "text": output.text,
        "candidates": [c.text for c in output.candidates],
        "images": [img.url for img in output.images],
        "metadata": output.metadata,  # útil p/ continuar a conversa
    }

class BatchIn(BaseModel):
    prompts: List[str]
    model: Optional[str] = None
    gem: Optional[str] = None

@app.post("/batch")
async def batch(req: BatchIn, request: Request):
    client: GeminiClient = request.app.state.gemini
    sem: asyncio.Semaphore = request.app.state.sem

    async def run_one(p: str):
        async with sem:
            out = await client.generate_content(
                prompt=p,
                model=req.model or Model.UNSPECIFIED,
                gem=req.gem,
            )
            return out.text

    results = await asyncio.gather(
        *(run_one(p) for p in req.prompts), return_exceptions=True
    )

    formatted = []
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            formatted.append({"index": i, "error": str(r)})
        else:
            formatted.append({"index": i, "text": r})

    return {"results": formatted}