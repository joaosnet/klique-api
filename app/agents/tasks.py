"""
Módulo para tarefas reutilizáveis do agente,
incluindo processamento de mensagens
e tarefas agendadas.
"""

from dataclasses import dataclass

from langchain_core.messages import HumanMessage
from loguru import logger

from ..services.whatsapp import WhatsAppService
from .agent import create_agent_runnable


@dataclass
class ProgressContext:
    """Contexto para gerenciar o progresso da mensagem."""

    whatsapp_service: WhatsAppService
    message_id: str
    user_number: str
    current_step: str


async def _update_progress(
    context: ProgressContext, text: str, new_step: str
) -> str:
    """Atualiza a mensagem de progresso se o passo mudou."""
    if context.message_id and context.current_step != new_step:
        logger.info(f'🔄 Atualizando progresso: {new_step} -> "{text}"')
        await context.whatsapp_service.edit_message(
            context.message_id, text, context.user_number
        )
        return new_step
    return context.current_step


async def _extract_final_response(node_data: dict) -> str | None:
    """Extrai a resposta final do nó do agente."""
    messages = node_data.get('messages', [])
    if not messages:
        return None

    last_msg = messages[-1]

    # Se não há tool_calls, é a resposta final
    has_content = hasattr(last_msg, 'content') and last_msg.content
    has_no_tools = not (
        hasattr(last_msg, 'tool_calls') and last_msg.tool_calls
    )

    if has_content and has_no_tools:
        return last_msg.content

    return None


async def _process_agent_node(
    node_data: dict, context: ProgressContext, tools_used: set
) -> str:
    """Processa eventos do nó 'agent'."""
    messages = node_data.get('messages', [])
    if not messages:
        logger.debug('   Nó agent sem mensagens')
        return context.current_step

    last_msg = messages[-1]
    logger.debug(f'   Última mensagem tipo: {type(last_msg).__name__}')

    # Detecta chamadas de ferramentas
    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
        tool_names = [tc['name'] for tc in last_msg.tool_calls]
        tools_used.update(tool_names)

        tools_text = ', '.join(tool_names)
        logger.info(f'🔧 Ferramentas detectadas: {tools_text}')
        new_step = await _update_progress(
            context, f'🔧 Usando ferramentas: {tools_text}...', 'tools'
        )
        return new_step

    # Detecta quando o agente está gerando resposta final
    if (
        hasattr(last_msg, 'content')
        and last_msg.content
        and not hasattr(last_msg, 'tool_calls')
    ):
        logger.info('✅ Resposta final detectada')
        return await _update_progress(
            context, '✅ Preparando resposta final...', 'finalizing'
        )

    return context.current_step


async def _process_stream_events(
    llm, message_text: str, user_number: str, progress_context: ProgressContext
) -> str | None:
    """Processa eventos do stream capturando
    apenas ferramentas e resposta final."""
    current_tool = None

    logger.info('🔄 Iniciando stream de eventos do agente...')

    # Usa astream_events com version="v2" para capturar eventos detalhados
    async for event in llm.astream_events(
        {'messages': [HumanMessage(content=message_text)]},
        config={'configurable': {'thread_id': user_number}},
        version='v2',
    ):
        kind = event['event']

        # Captura início de chamada de ferramenta
        if kind == 'on_tool_start':
            tool_name = event.get('name', 'unknown')
            current_tool = tool_name
            logger.info(f'🔧 Ferramenta iniciada: {tool_name}')
            progress_context.current_step = await _update_progress(
                progress_context, f'🔧 Executando: {tool_name}', 'tools'
            )

        # Captura resultado de ferramenta
        elif kind == 'on_tool_end':
            tool_name = event.get('name', current_tool or 'unknown')
            logger.info(f'⚙️ Ferramenta finalizada: {tool_name}')
            progress_context.current_step = await _update_progress(
                progress_context, '⚙️ Processando resultados...', 'processing'
            )
            current_tool = None

        # Captura conclusão do modelo
        elif kind == 'on_chat_model_end':
            logger.info('✅ Modelo finalizou geração')
            progress_context.current_step = await _update_progress(
                progress_context, '✅ Finalizando...', 'done'
            )

    logger.info('🏁 Stream finalizado, obtendo resposta final via ainvoke')
    return None


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
    progress_message_id = None

    try:
        logger.info(f'🤖 Mensagem recebida para o agente: "{message_text}"')

        # Envia mensagem de confirmação inicial
        progress_message_id = await whatsapp_service.send_message(
            user_number, '🤖 Mensagem recebida! Processando...'
        )
        logger.debug(
            f'📤 Mensagem de progresso enviada: {progress_message_id}'
        )

        # Cria o agente IA
        llm = await create_agent_runnable()

        # Atualiza status para "pensando"
        if progress_message_id:
            await whatsapp_service.edit_message(
                progress_message_id,
                '🧠 Analisando sua solicitação...',
                user_number,
            )

        # Variáveis para rastrear o progresso
        current_step = None

        # Cria contexto de progresso
        progress_context = ProgressContext(
            whatsapp_service=whatsapp_service,
            message_id=progress_message_id,
            user_number=user_number,
            current_step=current_step,
        )

        # Processa o stream e captura a resposta final
        final_response = await _process_stream_events(
            llm, message_text, user_number, progress_context
        )

        # Valida se capturamos a resposta final
        if not final_response:
            logger.warning(
                '⚠️ Resposta final não capturada do stream,'
                ' fazendo fallback para ainvoke'
            )
            resposta = await llm.ainvoke(
                {'messages': [HumanMessage(content=message_text)]},
                config={'configurable': {'thread_id': user_number}},
            )
            final_response = resposta['messages'][-1].content

        logger.info(f'🤖 Resposta do agente: "{final_response}"')

        # Substitui a mensagem de progresso pela resposta final
        if progress_message_id:
            await whatsapp_service.edit_message(
                progress_message_id, final_response, user_number
            )
        else:
            # Fallback: envia como nova mensagem
            await whatsapp_service.send_message(user_number, final_response)

        return {'status': 'ok', 'detail': 'processed_by_agent'}

    except Exception as e:
        logger.error(f'❌ Erro ao processar mensagem com agente: {e}')
        logger.exception('Detalhes do erro:')

        # Atualiza mensagem de progresso com erro
        if progress_message_id:
            try:
                await whatsapp_service.edit_message(
                    progress_message_id,
                    f'❌ Erro ao processar: {str(e)}',
                    user_number,
                )
            except Exception:
                pass

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
