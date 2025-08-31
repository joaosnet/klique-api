import asyncio
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Request
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

router = APIRouter()


class GenerateIn(BaseModel):
    prompt: str
    model: Optional[str] = (
        None  # ex: "gemini-1.5-flash" | "gemini-1.5-pro" | "unspecified"
    )
    gem: Optional[str] = None  # id de gem opcional
    files: Optional[List[str]] = None  # caminhos para arquivos opcionais
    chat_metadata: Optional[dict] = None  # para continuar conversa (opcional)


@router.post("/generate")
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