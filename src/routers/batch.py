import asyncio
from typing import List, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel

from gemini_webapi import GeminiClient
from gemini_webapi.constants import Model

router = APIRouter()


class BatchIn(BaseModel):
    prompts: List[str]
    model: Optional[str] = None
    gem: Optional[str] = None


@router.post("/batch")
async def batch(req: BatchIn, request: Request):
    """Processa múltiplos prompts em batch."""
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