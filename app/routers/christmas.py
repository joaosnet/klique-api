"""
Router para processamento de imagens natalinas.
Usa gemini-webapi para transformar fotos em avatares de Natal.
"""

import base64
import io
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image

from ..logger import logger

router = APIRouter(prefix='/api/christmas', tags=['christmas'])

# Prompts específicos para cada template de Natal
TEMPLATE_PROMPTS = {
    # Populares
    'papai-noel': (
        'Transform this person into Santa Claus with a red suit, white beard, '
        'and red hat with white trim. Keep their face recognizable but add '
        'rosy cheeks and a jolly expression. Christmas background with snow.'
    ),
    'duende': (
        'Transform this person into a Christmas elf with pointed ears, '
        'a green and red outfit with striped stockings, and a pointed hat '
        'with a bell. Cheerful toy workshop background.'
    ),
    'cena-natal': (
        'Place this person in a cozy Christmas scene with a decorated tree, '
        'fireplace, stockings, and warm lighting. Add festive atmosphere '
        'with snow visible through a window.'
    ),
    'gorro-neve': (
        'Add a cute winter beanie/snow hat with a pom-pom to this person. '
        'Add falling snowflakes around them and a winter wonderland background.'
    ),
    # Clássico
    'anjo': (
        'Transform this person into a beautiful Christmas angel with golden '
        'wings, white robes, and a glowing halo. Heavenly clouds background.'
    ),
    'rena': (
        'Transform this person into a cute reindeer with antlers decorated '
        'with Christmas lights, a red nose like Rudolph, and fuzzy ears.'
    ),
    'boneco-neve': (
        'Transform this person into a friendly snowman character with a '
        'carrot nose, coal eyes, scarf, and top hat. Snowy landscape.'
    ),
    'presente': (
        'Place this person as if emerging from a giant gift box with a big '
        'red bow. Festive wrapping paper and Christmas decorations around.'
    ),
    # Divertido
    'grinch': (
        'Transform this person into the Grinch character with green fur, '
        'a mischievous grin, and a Santa hat. Mount Crumpit background.'
    ),
    'pinguim': (
        'Transform this person into a cute Antarctic penguin wearing a '
        'Santa hat and red scarf. Icy winter wonderland background.'
    ),
    'urso-polar': (
        'Transform this person into a fluffy polar bear cub wearing '
        'a red bow tie and Santa hat. Arctic Christmas scene.'
    ),
    'biscoito': (
        'Transform this person into a decorated gingerbread cookie character '
        'with icing details, candy buttons, and a festive smile.'
    ),
    # Papai Noel variações
    'papai-noel-classico': (
        'Transform into the classic traditional Santa Claus from vintage '
        'Christmas cards. Red suit, round glasses, long white beard, warm smile.'
    ),
    'papai-noel-moderno': (
        'Transform into a modern, stylish Santa with a trimmed beard, '
        'trendy outfit variation, and contemporary festive accessories.'
    ),
    'papai-noel-tropical': (
        'Transform into a tropical beach Santa with Hawaiian shirt, '
        'sunglasses, flip-flops, and a palm tree Christmas background.'
    ),
    'papai-noel-festa': (
        'Transform into a party Santa with disco lights, confetti, '
        'champagne glass, and New Year celebration vibes.'
    ),
}

# Prompt padrão se o template não for encontrado
DEFAULT_PROMPT = (
    'Transform this person into a festive Christmas character. '
    'Add holiday decorations, winter clothing, and a magical Christmas atmosphere.'
)


def get_gemini_client(request: Request):
    """
    Obtém o cliente Gemini singleton armazenado em app.state.

    O cliente é inicializado uma única vez no lifespan da aplicação (main.py).
    """
    client = getattr(request.app.state, 'gemini_webapi_client', None)
    if client is None:
        raise HTTPException(
            status_code=503,
            detail='Serviço Gemini não está disponível. Verifique os cookies.',
        )
    return client


@router.post('/swap')
async def swap_face(
    request: Request,
    image: UploadFile = File(..., description='Imagem do usuário'),
    template: str = Form(..., description='ID do template selecionado'),
) -> JSONResponse:
    """
    Transforma a foto do usuário em um avatar natalino usando Gemini.

    Args:
        request: Request do FastAPI (para acessar app.state)
        image: Arquivo de imagem enviado pelo usuário
        template: ID do template (ex: 'papai-noel', 'duende', etc.)

    Returns:
        JSON com a imagem processada em base64
    """
    # Valida o tipo de arquivo
    if not image.content_type or not image.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400, detail='Arquivo deve ser uma imagem'
        )

    # Valida tamanho (max 10MB)
    contents = await image.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400, detail='Imagem deve ter no máximo 10MB'
        )

    try:
        # Salva a imagem temporariamente para enviar ao Gemini
        with tempfile.NamedTemporaryFile(
            suffix='.png', delete=False
        ) as temp_file:
            # Converte para PNG se necessário
            img = Image.open(io.BytesIO(contents))
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            img.save(temp_file, format='PNG')
            temp_path = temp_file.name

        # Obtém o prompt baseado no template
        prompt = TEMPLATE_PROMPTS.get(template, DEFAULT_PROMPT)
        full_prompt = (
            f'{prompt} '
            "Maintain the person's facial features and identity. "
            'High quality, detailed, 4K resolution, professional photography.'
        )

        logger.info(f'Processando imagem com template: {template}')
        logger.debug(f'Prompt: {full_prompt}')

        # Obtém o cliente Gemini singleton
        client = get_gemini_client(request)

        try:
            # Envia a imagem e o prompt para o Gemini
            response = await client.generate_content(
                full_prompt,
                files=[temp_path],
            )

            # Verifica se há imagens na resposta
            if response.images and len(response.images) > 0:
                # Salva a primeira imagem gerada
                output_dir = Path(tempfile.gettempdir())
                output_file = output_dir / f'christmas_{template}.png'

                await response.images[0].save(
                    path=str(output_dir),
                    filename=f'christmas_{template}.png',
                    verbose=False,
                )

                # Lê a imagem salva e converte para base64
                with open(output_file, 'rb') as f:
                    processed_bytes = f.read()

                img_base64 = base64.b64encode(processed_bytes).decode('utf-8')

                logger.success(f'Imagem processada com sucesso: {template}')

                return JSONResponse(
                    content={
                        'success': True,
                        'template': template,
                        'processed_image': f'data:image/png;base64,{img_base64}',
                    }
                )
            else:
                # Se não houver imagem, tenta usar o texto da resposta
                logger.warning(
                    'Nenhuma imagem gerada pelo Gemini, retornando original'
                )
                raise HTTPException(
                    status_code=500,
                    detail='Não foi possível gerar a imagem transformada',
                )

        finally:
            # Limpa arquivo temporário
            Path(temp_path).unlink(missing_ok=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Erro ao processar imagem: {e}')
        raise HTTPException(
            status_code=500, detail=f'Erro ao processar imagem: {e!s}'
        )
