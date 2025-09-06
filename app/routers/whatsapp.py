from fastapi import APIRouter, Depends, HTTPException, Request
from rich import print

from ..services.gemini import GeminiService, get_gemini_service
from ..services.whatsapp import WhatsAppService

router = APIRouter(
    prefix='/webhooks',
    tags=['webhooks'],
)


@router.post('/whatsapp')
async def receive_whatsapp_webhook(
    request: Request,
    gemini_service: GeminiService = Depends(get_gemini_service),
):
    """
    Recebe e processa os webhooks enviados pelo serviço go-whatsapp.
    """
    whatsapp_service = None
    try:
        data = await request.json()
        print('[bold green]Webhook do WhatsApp recebido:[/bold green]')
        print(data)

        # Extrai o prompt da mensagem de texto ou da legenda da imagem
        prompt = data.get('message', {}).get('text')
        if not prompt and 'image' in data:
            prompt = data.get('image', {}).get('caption')

        if not prompt:
            print(
                '[bold yellow]Não foi possível encontrar um '
                'prompt no webhook (texto ou legenda).[/bold yellow]'
            )
            return {'status': 'ok', 'info': 'Nenhum prompt encontrado.'}

        print(f'Prompt extraído: [cyan]{prompt}[/cyan]')

        # Extrai o número de telefone do remetente
        sender_phone = data.get('sender_id')

        if not sender_phone:
            print(
                '[bold yellow]Não foi possível encontrar o '
                'número do remetente.[/bold yellow]'
            )
            return {
                'status': 'ok',
                'info': 'Número do remetente não encontrado.',
            }
        whatsapp_service = WhatsAppService()
        image_bytes = None
        media_path = data.get('image', {}).get('media_path')
        if media_path:
            image_bytes = await whatsapp_service.download_media(media_path)
        generated_bytes = await gemini_service.generate_image_from_prompt(
            prompt, image_bytes
        )

        if not generated_bytes:
            raise HTTPException(
                status_code=500, detail='Falha ao gerar a imagem.'
            )

        print(
            '[bold green]Imagem gerada com sucesso!'
            'Enviando para o WhatsApp...[/bold green]'
        )

        send_result = await whatsapp_service.send_image_message(
            phone_number=sender_phone,
            image_bytes=generated_bytes,
            caption=f"Sua imagem gerada a partir de: '{prompt}'",
        )

        if not send_result:
            raise HTTPException(
                status_code=500,
                detail='Falha ao enviar a imagem para o WhatsApp.',
            )

        print('[bold green]Enviando status para o WhatsApp...[/bold green]')
        # Posta a imagem no status
        await whatsapp_service.post_status_update(
            image_bytes=generated_bytes,
            caption=f"Gerado por Klique AI: '{prompt}'",
        )
        print('[bold green]Status postado com sucesso![/bold green]')

        return {
            'status': 'ok',
            'detail': 'Imagem enviada com sucesso e status postado!',
        }
    except Exception as e:
        print(f'[bold red]Erro ao processar webhook:[/bold red] {e}')
        raise HTTPException(
            status_code=500, detail='Erro interno ao processar o webhook.'
        )
    finally:
        if whatsapp_service:
            await whatsapp_service.close()
            print(
                '[bold blue]Conexão com WhatsAppService fechada.[/bold blue]'
            )
