import asyncio
import base64
import io
import logging
import uuid
from typing import Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from gemini_webapi import ChatSession, GeminiClient
from gemini_webapi.constants import Model
from gemini_webapi.exceptions import (
    APIError,
    ModelInvalid,
    TemporarilyBlocked,
    TimeoutError,
    UsageLimitExceeded,
)
from PIL import Image
from pydantic import BaseModel

from src.services.gemini import GeminiService

router = APIRouter()


class GenerateIn(BaseModel):
    prompt: str
    model: Optional[str] = (
        None  # ex: "gemini-1.5-flash" | "gemini-1.5-pro" | "unspecified"
    )
    gem: Optional[str] = None  # id de gem opcional
    files: Optional[List[str]] = None  # caminhos para arquivos opcionais
    chat_metadata: Optional[dict] = None  # para continuar conversa (opcional)


@router.post('/generate')
async def generate(req: GenerateIn, request: Request):
    """Gera conteúdo baseado em um prompt, com suporte opcional
    para arquivos e metadados de chat."""
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
        'text': output.text,
        'candidates': [c.text for c in output.candidates],
        'images': [img.url for img in output.images],
        'metadata': output.metadata,  # útil p/ continuar a conversa
    }


@router.post('/generate/image')
async def generate_image(
    request: Request,
    prompt: str = Form(...),
    session_id: Optional[str] = Form(None),
    image_file: Optional[UploadFile] = File(None),
):
    """Gera uma imagem a partir de um prompt,
    opcionalmente continuando uma sessão de chat existente."""
    gemini_service: GeminiService = request.app.state.gemini_service
    chat_sessions: Dict[str, ChatSession] = request.app.state.chat_sessions
    chat_session = None

    if session_id and session_id in chat_sessions:
        chat_session = chat_sessions[session_id]
    else:
        chat_session = await gemini_service.start_chat()
        new_session_id = str(uuid.uuid4())
        chat_sessions[new_session_id] = chat_session
        session_id = new_session_id

    image = None
    if image_file:
        contents = await image_file.read()
        image = Image.open(io.BytesIO(contents))

    try:
        response = await gemini_service.send_message(
            chat=chat_session, prompt=prompt, image=image
        )

        generated_image_base64 = None
        if response.images:
            # Assumindo que a imagem gerada está em response.images[0]
            # e que é um objeto com um método para obter os bytes
            img_buffer = io.BytesIO()
            await response.images[0].save(img_buffer)
            img_bytes = img_buffer.getvalue()
            generated_image_base64 = base64.b64encode(img_bytes).decode(
                'utf-8'
            )

        return {
            'session_id': session_id,
            'generated_image': generated_image_base64,
            'response_text': response.text,
        }
    except Exception as e:
        logging.error(f'Erro inesperado em generate_image: {e}', exc_info=True)
        raise HTTPException(
            status_code=500, detail=f'Erro interno no servidor: {e}'
        )
