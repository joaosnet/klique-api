from langchain_core.messages import HumanMessage
from loguru import logger

from .agent import AgentCache


async def process_message_with_agent(
    user_number: str,
    message_text: str,
    whatsapp_service,
) -> dict:
    """Processa uma mensagem usando o agente LangGraph e envia a resposta via WhatsApp."""
    try:
        agent = await AgentCache.get_agent()

        config = {'configurable': {'thread_id': user_number}}
        input_messages = {'messages': [HumanMessage(content=message_text)]}

        logger.info(
            f'🤖 Processando mensagem do usuário {user_number}: '
            f'{message_text[:100]}...'
        )

        result = await agent.ainvoke(input_messages, config=config)

        messages = result.get('messages', [])
        if not messages:
            logger.warning('⚠️ Agente não retornou mensagens')
            return {'status': 'error', 'detail': 'no_response'}

        last_message = messages[-1]
        response_text = (
            last_message.content
            if isinstance(last_message.content, str)
            else str(last_message.content)
        )

        logger.info(f'✅ Resposta gerada: {response_text[:100]}...')

        await whatsapp_service.send_message(user_number, response_text)

        return {'status': 'ok', 'detail': 'message_processed'}

    except Exception as e:
        logger.error(f'❌ Erro ao processar mensagem com agente: {e}')
        raise
