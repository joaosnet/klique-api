import asyncio
import base64
import io
from typing import List

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from PIL import Image
from pydantic import BaseModel

from src.logger import logger
from src.services.gemini import GeminiService


router = APIRouter()


class BatchImageGenerationResponse(BaseModel):
    generated_image: str
    response_text: str


@router.post(
    "/batch/generate/image",
    response_model=List[BatchImageGenerationResponse],
    summary="Gera múltiplas imagens em lote a partir de uma imagem base e vários prompts.",
)
async def batch_generate_image(
    request: Request,
    prompts: List[str] = Form(..., description="Uma lista de prompts de texto para gerar as imagens."),
    image: UploadFile = File(..., description="A imagem base para as edições."),
):
    """
    Este endpoint recebe uma única imagem e uma lista de prompts para gerar
    múltiplas versões da imagem em um único processo em lote.

    - **prompts**: Uma lista de strings, cada uma sendo um prompt para o modelo.
    - **image**: O arquivo de imagem a ser usado como base para todas as gerações.

    A função utiliza `asyncio.gather` para processar todas as solicitações de
    geração de imagem de forma concorrente, otimizando o tempo de resposta.
    """
    gemini_service: GeminiService = request.app.state.gemini_service
    sem: asyncio.Semaphore = request.app.state.sem

    try:
        image_bytes = await image.read()
        pil_image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        logger.error(f"Erro ao processar o upload da imagem: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo de imagem inválido.",
        )

    async with sem:
        results = await gemini_service.batch_generate_images(
            prompts=prompts, image=pil_image
        )

    processed_results = []
    for i, res in enumerate(results):
        if isinstance(res, Exception):
            logger.error(
                f"Erro no processamento em lote para o prompt '{prompts[i]}': {res}",
                exc_info=True,
            )
            # Opcional: decidir se um erro em um item deve falhar a requisição inteira
            # ou apenas ser omitido/marcado na resposta.
            # Aqui, vamos pular os resultados com erro.
            continue

        if not res.images:
            logger.warning(f"Nenhuma imagem gerada para o prompt: '{prompts[i]}'")
            continue

        try:
            # Pega a primeira imagem gerada
            generated_image = res.images[0]
            
            # Converte a imagem para base64
            buffer = io.BytesIO()
            generated_image.save(fp=buffer, format="PNG")
            img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

            processed_results.append(
                BatchImageGenerationResponse(
                    generated_image=img_base64,
                    response_text=res.text,
                )
            )
        except Exception as e:
            logger.error(
                f"Erro ao processar a imagem gerada para o prompt '{prompts[i]}': {e}",
                exc_info=True,
            )

    if not processed_results:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Nenhuma imagem pôde ser gerada com sucesso.",
        )

    return processed_results