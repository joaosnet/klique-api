import asyncio
import base64
import io
import uuid
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    Security,
    Header,
)
from fastapi.security import HTTPBearer
from PIL import Image

from src.services.gemini import GeminiService
from src.services.firebase_service import FirebaseService
from src.services.drive_service import DriveService
from src.services.mongo_service import MongoService
from src.logger import logger

router = APIRouter()
auth_scheme = HTTPBearer()


@router.post("/generate/image")
async def generate_image(
    request: Request,
    prompt: str = Form(...),
    image_file: Optional[UploadFile] = File(None),
    authorization: Optional[str] = Header(None),
):
    # Extrair serviços do estado da aplicação
    firebase_service: FirebaseService = request.app.state.firebase_service
    mongo_service: MongoService = request.app.state.mongo_service
    drive_service: DriveService = request.app.state.drive_service
    gemini_service: GeminiService = request.app.state.gemini_service

    # 1. Autenticação e Extração do Token
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        # O cabeçalho vem como "Bearer <token>", então pegamos a segunda parte
        token = authorization.split(" ")[1]
        user_data = firebase_service.verify_firebase_token(token)
        uid = user_data["uid"]
        logger.info(f"Usuário autenticado com sucesso: {uid}")
    except IndexError:
        raise HTTPException(
            status_code=401, detail="Invalid Authorization header format"
        )
    except HTTPException as e:
        logger.warning(f"Falha na autenticação: {e.detail}")
        raise e

    # 2. Verificação de Limite de Uso
    if await mongo_service.is_rate_limited(uid):
        raise HTTPException(status_code=429, detail="Limite de uso excedido.")

    # 3. Geração de Imagem
    image = None
    if image_file:
        contents = await image_file.read()
        image = Image.open(io.BytesIO(contents))

    try:
        # Inicia uma nova sessão de chat para cada requisição, já que não há estado
        chat_session = await gemini_service.start_chat()

        response = await gemini_service.send_message(
            chat=chat_session, prompt=prompt, image=image
        )

        if not response.images:
            raise HTTPException(status_code=500, detail="Nenhuma imagem foi gerada.")

        generated_image = response.images[0]
        
        # Converte a imagem para bytes para upload e para a resposta
        img_buffer = io.BytesIO()
        await generated_image.save(img_buffer, format="JPEG")
        img_bytes = img_buffer.getvalue()

        # 4. Upload para o Google Drive
        filename = f"{uid}_{uuid.uuid4()}.jpg"
        drive_file_id = drive_service.upload_image(
            user_id=uid, image_bytes=img_bytes, filename=filename
        )
        logger.info(f"Imagem carregada para o Drive com ID: {drive_file_id}")

        # 5. Salvar Prompt e Metadados no MongoDB
        await mongo_service.save_prompt(
            user_id=uid,
            prompt_text=prompt,
            drive_file_id=drive_file_id,
        )
        logger.info(f"Prompt salvo para o usuário: {uid}")

        # 6. Retornar a Imagem Gerada em Base64 e o ID do Drive
        encoded_image = base64.b64encode(img_bytes).decode("utf-8")

        return {
            "generated_image": encoded_image,
            "drive_file_id": drive_file_id,
            "response_text": response.text,
            "session_id": chat_session.session_id,
        }

    except Exception as e:
        logger.error(f"Erro inesperado em generate_image para o usuário {uid}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {e}")
