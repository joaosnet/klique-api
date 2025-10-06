"""
Módulo para tarefas reutilizáveis do agente,
incluindo processamento de mensagens
e tarefas agendadas.
"""

from langchain_core.messages import HumanMessage
from loguru import logger

from ..services.whatsapp import WhatsAppService
from .agent import create_agent_runnable


async def process_message_with_agent(
    user_number: str,
    message_text: str,
    whatsapp_service: WhatsAppService,
) -> dict:
    """
    Processa uma mensagem com o agente IA e envia a resposta via WhatsApp.

    Esta função é reutilizável tanto para webhooks quanto
    para tarefas agendadas.

    :param user_number: Número do usuário no WhatsApp
    :param message_text: Texto da mensagem a ser processada
    :param whatsapp_service: Instância do serviço WhatsApp
    :return: Dicionário com status e detalhes da operação
    """
    try:
        logger.info(f'🤖 Mensagem recebida para o agente: "{message_text}"')

        # Cria o agente IA
        llm = await create_agent_runnable()

        # Processa a mensagem
        resposta = await llm.ainvoke(
            {'messages': [HumanMessage(content=message_text)]},
            config={'configurable': {'thread_id': user_number}},
        )

        final_response = resposta['messages'][-1].content
        logger.info(f'🤖 Resposta do agente: "{final_response}"')

        # Envia a resposta via WhatsApp
        await whatsapp_service.send_message(user_number, final_response)

        return {'status': 'ok', 'detail': 'processed_by_agent'}

    except Exception as e:
        logger.error(f'❌ Erro ao processar mensagem com agente: {e}')
        logger.exception('Detalhes do erro:')
        return {'status': 'error', 'detail': str(e)}


async def trigger_sigaa_summary_agent(
    user_number: str,
    whatsapp_service: WhatsAppService,
) -> dict:
    """
    Tarefa agendada para enviar resumo dos avisos do SIGAA via agente.

    Esta função é chamada diariamente às 12:00 para gerar e enviar
    um resumo dos avisos do SIGAA através do agente IA.

    :param user_number: Número do usuário destinatário
    :param whatsapp_service: Instância do serviço WhatsApp
    :return: Dicionário com status da operação
    """
    try:
        logger.info('📅 Iniciando tarefa agendada: resumo dos avisos do SIGAA')

        # Prompt para o agente buscar os avisos do SIGAA
        prompt = 'Faça um resumo dos avisos do SIGAA das minhas turmas'

        # Processa com o agente
        result = await process_message_with_agent(
            user_number=user_number,
            message_text=prompt,
            whatsapp_service=whatsapp_service,
        )

        if result['status'] == 'ok':
            logger.success('✅ Resumo dos avisos do SIGAA enviado com sucesso')
        else:
            logger.error(
                f'❌ Falha ao enviar resumo dos avisos: {result["detail"]}'
            )

        return result

    except Exception as e:
        logger.error(f'❌ Erro na tarefa agendada do SIGAA: {e}')
        logger.exception('Detalhes do erro:')
        return {'status': 'error', 'detail': str(e)}
