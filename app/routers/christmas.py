"""
Router para processamento de imagens natalinas.
Usa gemini-webapi para transformar fotos em avatares de Natal.
Suporta Server-Sent Events (SSE) para updates de progresso.
"""

import asyncio
import base64
import io
import json
import tempfile
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from typing import Optional
from fastapi.responses import JSONResponse, StreamingResponse
from PIL import Image

from ..dependencies import get_current_user_optional
from ..logger import logger
from ..services.image_cleaner import remove_background, remove_signature
from .credits import check_user_has_credits, use_one_credit

router = APIRouter(prefix='/api/christmas', tags=['christmas'])

# Prompts específicos para cada template de Natal
TEMPLATE_PROMPTS = {
    # Populares
    'papai-noel': (
        'Transform this person into Santa Claus with a red suit, white '
        'beard, and red hat with white trim. Keep their face recognizable '
        'but add rosy cheeks and a jolly expression. Christmas background.'
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
        'Add falling snowflakes around them and a winter wonderland.'
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
        'Christmas cards. Red suit, round glasses, long white beard.'
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

# Configuração de categorias e templates para o frontend
TEMPLATES_CONFIG = {
    'populares': [
        {
            'id': 'papai-noel',
            'name': 'Papai Noel',
            'emoji': '🎅',
            'preview_url': None,
        },
        {'id': 'duende', 'name': 'Duende', 'emoji': '🧝', 'preview_url': None},
        {
            'id': 'cena-natal',
            'name': 'Cena de Natal',
            'emoji': '🎄',
            'preview_url': None,
        },
        {
            'id': 'gorro-neve',
            'name': 'Gorro de Neve',
            'emoji': '⛄',
            'preview_url': None,
        },
    ],
    'classico': [
        {'id': 'anjo', 'name': 'Anjo', 'emoji': '👼', 'preview_url': None},
        {'id': 'rena', 'name': 'Rena', 'emoji': '🦌', 'preview_url': None},
        {
            'id': 'boneco-neve',
            'name': 'Boneco de Neve',
            'emoji': '☃️',
            'preview_url': None,
        },
        {
            'id': 'presente',
            'name': 'Presente',
            'emoji': '🎁',
            'preview_url': None,
        },
    ],
    'divertido': [
        {'id': 'grinch', 'name': 'Grinch', 'emoji': '💚', 'preview_url': None},
        {
            'id': 'pinguim',
            'name': 'Pinguim',
            'emoji': '🐧',
            'preview_url': None,
        },
        {
            'id': 'urso-polar',
            'name': 'Urso Polar',
            'emoji': '🐻‍❄️',
            'preview_url': None,
        },
        {
            'id': 'biscoito',
            'name': 'Biscoito',
            'emoji': '🍪',
            'preview_url': None,
        },
    ],
    'papai-noel': [
        {
            'id': 'papai-noel-classico',
            'name': 'Clássico',
            'emoji': '🎅',
            'preview_url': None,
        },
        {
            'id': 'papai-noel-moderno',
            'name': 'Moderno',
            'emoji': '🎅',
            'preview_url': None,
        },
        {
            'id': 'papai-noel-tropical',
            'name': 'Tropical',
            'emoji': '🌴',
            'preview_url': None,
        },
        {
            'id': 'papai-noel-festa',
            'name': 'Festa',
            'emoji': '🎉',
            'preview_url': None,
        },
    ],
}

# Prompt padrão se o template não for encontrado
DEFAULT_PROMPT = (
    'Transform this person into a festive Christmas character. '
    'Add holiday decorations, winter clothing, and magical Christmas.'
)


@router.get('/templates')
async def get_templates():
    """Retorna as categorias e templates disponíveis."""
    return TEMPLATES_CONFIG


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


async def generate_sse_event(event: str, data: dict) -> str:
    """Formata um evento SSE para streaming."""
    return f'event: {event}\ndata: {json.dumps(data)}\n\n'


async def process_image_with_progress(
    client,
    temp_path: str,
    template: str,
    prompt: str,
    remove_bg: bool = False,
):
    """
    Processa imagem com Gemini e gera eventos de progresso.

    Yields:
        Eventos SSE com progresso e resultado final.
    """
    output_file = None

    try:
        # Total de etapas: 4 base + 1 (watermark) + 1 (bg opcional)
        total_steps = 6 if remove_bg else 5

        # Etapa 1: Preparando
        yield await generate_sse_event(
            'progress',
            {
                'step': 1,
                'total': total_steps,
                'message': '🎄 Preparando sua foto...',
                'percent': 10,
            },
        )
        await asyncio.sleep(0.5)

        # Etapa 2: Enviando para o Gemini
        yield await generate_sse_event(
            'progress',
            {
                'step': 2,
                'total': total_steps,
                'message': '✨ Enviando para a magia do Natal...',
                'percent': 20,
            },
        )

        # Etapa 3: Gerando (pode demorar)
        yield await generate_sse_event(
            'progress',
            {
                'step': 3,
                'total': total_steps,
                'message': '🎅 Transformando você em personagem natalino...',
                'percent': 40,
            },
        )

        # Chama o Gemini
        response = await client.generate_content(
            prompt,
            files=[temp_path],
        )

        # Etapa 4: Salvando imagem
        yield await generate_sse_event(
            'progress',
            {
                'step': 4,
                'total': total_steps,
                'message': '💾 Salvando imagem gerada...',
                'percent': 60,
            },
        )

        # Verifica se há imagens na resposta
        if response.images and len(response.images) > 0:
            output_dir = Path(tempfile.gettempdir())
            output_file = output_dir / f'christmas_{template}.png'

            await response.images[0].save(
                path=str(output_dir),
                filename=f'christmas_{template}.png',
                verbose=False,
            )

            # Etapa 5: Removendo marca d'água do Gemini
            yield await generate_sse_event(
                'progress',
                {
                    'step': 5,
                    'total': total_steps,
                    'message': "🧹 Removendo marca d'água...",
                    'percent': 75,
                },
            )

            # Remove watermark usando remove_signature
            cleaned_path, status = remove_signature(
                str(output_file),
                output_path=str(
                    output_dir / f'christmas_{template}_clean.png'
                ),
            )

            if cleaned_path:
                output_file = Path(cleaned_path)
                logger.debug(f"Marca d'água removida: {status}")

            # Etapa 6: Remoção de fundo (opcional)
            if remove_bg:
                yield await generate_sse_event(
                    'progress',
                    {
                        'step': 6,
                        'total': total_steps,
                        'message': '✂️ Removendo fundo da imagem...',
                        'percent': 85,
                    },
                )

                nobg_path, bg_status = remove_background(
                    str(output_file),
                    output_path=str(
                        output_dir / f'christmas_{template}_nobg.png'
                    ),
                )

                if nobg_path:
                    output_file = Path(nobg_path)
                    logger.debug(f'Fundo removido: {bg_status}')

            # Lê a imagem final e converte para base64
            with open(output_file, 'rb') as f:
                processed_bytes = f.read()

            img_base64 = base64.b64encode(processed_bytes).decode('utf-8')

            logger.success(f'Imagem processada com sucesso: {template}')

            yield await generate_sse_event(
                'complete',
                {
                    'success': True,
                    'template': template,
                    'processed_image': f'data:image/png;base64,{img_base64}',
                    'message': '🎉 Transformação completa!',
                },
            )
        else:
            logger.warning('Nenhuma imagem gerada pelo Gemini')
            yield await generate_sse_event(
                'error',
                {
                    'success': False,
                    'message': 'Não foi possível gerar a imagem transformada',
                },
            )

    except Exception as e:
        logger.error(f'Erro ao processar imagem: {e}')
        yield await generate_sse_event(
            'error',
            {
                'success': False,
                'message': f'Erro ao processar: {e!s}',
            },
        )

    finally:
        # Limpa arquivos temporários
        if output_file and output_file.exists():
            output_file.unlink(missing_ok=True)


@router.post('/swap')
async def swap_face(
    request: Request,
    image: UploadFile = File(..., description='Imagem do usuário'),
    template: str = Form(..., description='ID do template selecionado'),
    remove_bg: bool = Form(
        False, description='Remover fundo da imagem gerada'
    ),
) -> JSONResponse:
    """
    Transforma a foto do usuário em um avatar natalino usando Gemini.

    A imagem gerada terá a marca d'água do Gemini removida automaticamente.

    Args:
        request: Request do FastAPI (para acessar app.state)
        image: Arquivo de imagem enviado pelo usuário
        template: ID do template (ex: 'papai-noel', 'duende', etc.)
        remove_bg: Se True, remove o fundo da imagem gerada

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
            'High quality, detailed, 4K resolution, professional.'
        )

        logger.info(f'Processando imagem com template: {template}')

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
                output_dir = Path(tempfile.gettempdir())
                output_file = output_dir / f'christmas_{template}.png'

                await response.images[0].save(
                    path=str(output_dir),
                    filename=f'christmas_{template}.png',
                    verbose=False,
                )

                # Remove marca d'água do Gemini
                logger.debug("Removendo marca d'água...")
                cleaned_path, status = remove_signature(
                    str(output_file),
                    output_path=str(
                        output_dir / f'christmas_{template}_clean.png'
                    ),
                )

                if cleaned_path:
                    output_file = Path(cleaned_path)
                    logger.debug(f"Marca d'água removida: {status}")

                # Remove fundo (opcional)
                if remove_bg:
                    logger.debug('Removendo fundo...')
                    nobg_path, bg_status = remove_background(
                        str(output_file),
                        output_path=str(
                            output_dir / f'christmas_{template}_nobg.png'
                        ),
                    )

                    if nobg_path:
                        output_file = Path(nobg_path)
                        logger.debug(f'Fundo removido: {bg_status}')

                # Lê a imagem final e converte para base64
                with open(output_file, 'rb') as f:
                    processed_bytes = f.read()

                img_base64 = base64.b64encode(processed_bytes).decode('utf-8')

                logger.success(f'Imagem processada: {template}')

                return JSONResponse(
                    content={
                        'success': True,
                        'template': template,
                        'processed_image': (
                            f'data:image/png;base64,{img_base64}'
                        ),
                    }
                )
            else:
                logger.warning('Nenhuma imagem gerada pelo Gemini')
                raise HTTPException(
                    status_code=500,
                    detail='Não foi possível gerar a imagem',
                )

        finally:
            Path(temp_path).unlink(missing_ok=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Erro ao processar imagem: {e}')
        raise HTTPException(
            status_code=500, detail=f'Erro ao processar imagem: {e!s}'
        )


@router.post('/swap-stream')
async def swap_face_stream(
    request: Request,
    image: UploadFile = File(..., description='Imagem do usuário'),
    template: str = Form(..., description='ID do template selecionado'),
    remove_bg: bool = Form(
        False, description='Remover fundo da imagem gerada'
    ),
    current_user: Optional[dict] = Depends(get_current_user_optional),
) -> StreamingResponse:
    """
    Transforma a foto com streaming de progresso via SSE.

    Permite primeiro uso sem login (vincular ao IP).
    Requer créditos se já usado.
    A imagem gerada terá a marca d'água do Gemini removida automaticamente.

    Args:
        request: Request do FastAPI
        image: Arquivo de imagem enviado pelo usuário
        template: ID do template selecionado
        remove_bg: Se True, remove o fundo da imagem gerada
        current_user: Usuário autenticado (opcional)

    Returns:
        StreamingResponse com eventos SSE de progresso
    """
    # Identifica o usuário (se logado) ou o IP (se guest)
    if current_user:
        user_id = str(current_user.get('_id'))
        is_guest = False
    else:
        # Tenta pegar o IP real do cliente (especialmente se atrás de proxy como ngrok/nginx)
        client_ip = (
            request.headers.get('x-forwarded-for') or request.client.host
        )
        user_id = f'guest_{client_ip}'
        is_guest = True
        logger.info(f'Processamento via guest IP: {client_ip}')

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

    # Valida créditos do usuário
    credits_check = await check_user_has_credits(user_id)

    if not credits_check['has_credits']:
        if is_guest:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Créditos iniciais usados. Faça login para ganhar mais créditos!',
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail='Créditos insuficientes. Compre mais créditos.',
            )

    # Consome 1 crédito antes de processar
    credit_result = await use_one_credit(user_id)
    if not credit_result['success']:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=credit_result['message'],
        )

    # Salva a imagem temporariamente
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        img = Image.open(io.BytesIO(contents))
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        img.save(temp_file, format='PNG')
        temp_path = temp_file.name

    # Obtém o prompt
    prompt = TEMPLATE_PROMPTS.get(template, DEFAULT_PROMPT)
    full_prompt = (
        f'{prompt} '
        "Maintain the person's facial features and identity. "
        'High quality, detailed, 4K resolution, professional.'
    )

    logger.info(f'Processando imagem (SSE) com template: {template}')

    # Obtém o cliente Gemini
    client = get_gemini_client(request)

    async def cleanup_and_stream():
        """Stream com cleanup do arquivo temporário."""
        try:
            async for event in process_image_with_progress(
                client, temp_path, template, full_prompt, remove_bg
            ):
                yield event
        finally:
            Path(temp_path).unlink(missing_ok=True)

    return StreamingResponse(
        cleanup_and_stream(),
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
        },
    )
