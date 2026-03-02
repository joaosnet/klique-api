import json
import base64
import re
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    UploadFile,
    File,
)
from ..dependencies import get_current_active_user
from ..logger import logger

router = APIRouter(prefix='/api/models', tags=['models'])


@router.post('/generate-svg')
async def generate_svg_from_image(
    request: Request,
    file: UploadFile = File(...),
    current_user=Depends(get_current_active_user),
):
    """
    Receives an image of a card design and uses Gemini to generate a clean,
    responsive SVG implementation.
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400, detail='O ficheiro deve ser uma imagem.'
        )

    gemini_client = getattr(request.app.state, 'gemini_webapi_client', None)
    if not gemini_client:
        raise HTTPException(
            status_code=503,
            detail='Motor de IA (Gemini) não está configurado.',
        )

    try:
        # Read file contents and prepare for Gemini
        file_bytes = await file.read()

        prompt = """
        You are an expert Frontend Developer and UI Designer. 
        I have provided an image of a card design. 
        Your task is to analyze the visual structure, layout, typography, colors, and stylistic elements of this card, 
        and output a CLEAN, RESPONSIVE, and REUSABLE SVG markup that faithfully replicates this design.
        
        The SVG should act as a background/template.
        Use viewBox="0 0 400 600" (or similar standard card ratio).
        Use standard SVG elements (<defs>, <linearGradient>, <rect>, <path>, <text>).
        Ensure it is visually stunning and modern.
        
        Return ONLY valid JSON containing the "svg" string property.
        Example response format:
        {
          "svg": "<svg viewBox=\\"0 0 400 600\\">...</svg>"
        }
        """

        # We pass the image alongside the text prompt.
        logger.info('Enviando imagem para o Gemini para gerar modelo SVG...')
        response = await gemini_client.generate_content([prompt, file_bytes])

        raw_text = response.text.strip()

        # Extract JSON
        json_match = re.search(r'\{[\s\S]*\}', raw_text)
        if not json_match:
            logger.error(
                f'Gemini não retornou JSON válido. Texto raw: {raw_text[:200]}'
            )
            raise HTTPException(
                status_code=500,
                detail='Falha ao gerar o modelo SVG. Tente novamente com outra imagem.',
            )

        result_dict = json.loads(json_match.group(0))
        svg_code = result_dict.get('svg', '')

        if not svg_code or not svg_code.startswith('<svg'):
            raise HTTPException(
                status_code=500, detail='SVG gerado é inválido.'
            )

        return {'success': True, 'svg': svg_code}

    except json.JSONDecodeError as e:
        logger.error(f'Erro ao interpretar resposta SVG do Gemini: {e}')
        raise HTTPException(
            status_code=500,
            detail='Erro interno ao processar a resposta da IA.',
        )
    except Exception as e:
        logger.error(f'Erro ao gerar modelo SVG: {e}')
        raise HTTPException(status_code=500, detail=str(e))
