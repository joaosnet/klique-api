from fastapi import APIRouter, HTTPException, Request
from rich import print

from src.services.gemini_app import GeminiAppService
from src.services.whatsapp import WhatsAppService

router = APIRouter(
    prefix='/webhooks',
    tags=['webhooks'],
)


@router.post('/whatsapp')
async def receive_whatsapp_webhook(request: Request):
    """
    Recebe e processa os webhooks enviados pelo serviço go-whatsapp.
    """
    try:
        data = await request.json()
        print('[bold green]Webhook do WhatsApp recebido:[/bold green]')
        print(data)

        # Extrai o prompt da mensagem
        # A estrutura exata do JSON pode precisar de ajuste.
        prompt = (
            data.get('text')
            or (data.get('message') and data['message'].get('body'))
            or (
                data.get('data')
                and data['data'].get('message')
                and data['data']['message'].get('body')
            )
        )

        if not prompt:
            print(
                '[bold yellow]Não foi possível encontrar um prompt no webhook.[/bold yellow]'
            )
            return {'status': 'ok', 'info': 'Nenhum prompt encontrado.'}

        print(f'Prompt extraído: [cyan]{prompt}[/cyan]')

        # Extrai o número de telefone do remetente
        sender_phone = data.get('from') or (
            data.get('sender') and data['sender'].get('id')
        )

        if not sender_phone:
            print(
                '[bold yellow]Não foi possível encontrar o número do remetente.[/bold yellow]'
            )
            return {
                'status': 'ok',
                'info': 'Número do remetente não encontrado.',
            }

        gemini_service = GeminiAppService()
        image_bytes = await gemini_service.generate_image_from_prompt(prompt)

        if not image_bytes:
            raise HTTPException(
                status_code=500, detail='Falha ao gerar a imagem.'
            )

        print(
            '[bold green]Imagem gerada com sucesso! Enviando para o WhatsApp...[/bold green]'
        )

        whatsapp_service = WhatsAppService()
        send_result = await whatsapp_service.send_image_message(
            phone_number=sender_phone,
            image_bytes=image_bytes,
            caption=f"Sua imagem gerada a partir de: '{prompt}'",
        )
        await whatsapp_service.close()

        if not send_result:
            raise HTTPException(
                status_code=500,
                detail='Falha ao enviar a imagem para o WhatsApp.',
            )

        # TODO: Implementar a lógica para postar no status.

        return {'status': 'ok', 'detail': 'Imagem enviada com sucesso!'}
    except Exception as e:
        print(f'[bold red]Erro ao processar webhook:[/bold red] {e}')
        raise HTTPException(
            status_code=500, detail='Erro interno ao processar o webhook.'
        )
