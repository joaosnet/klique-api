"""
Módulo para tarefas reutilizáveis do agente,
incluindo processamento de mensagens
e tarefas agendadas.
"""

from dataclasses import dataclass
from pathlib import Path

from langchain_core.messages import HumanMessage
from loguru import logger

from ..services.whatsapp import WhatsAppService
from .agent import create_agent_runnable

# Diretório base para prompts
PROMPTS_DIR = Path(__file__).parent / 'prompts'


def _load_prompt(filename: str) -> str:
    """
    Carrega um prompt de um arquivo Markdown.

    :param filename: Nome do arquivo (ex: 'instagram_post.md')
    :return: Conteúdo do prompt
    """
    prompt_path = PROMPTS_DIR / filename
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.error(f'❌ Arquivo de prompt não encontrado: {prompt_path}')
        raise
    except Exception as e:
        logger.error(f'❌ Erro ao carregar prompt {filename}: {e}')
        raise


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

        # Carrega prompt do arquivo
        prompt = _load_prompt('sigaa_summary.md')

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


async def trigger_instagram_post_agent(
    user_number: str,
    whatsapp_service: WhatsAppService,
) -> dict:
    """
    Tarefa agendada para criar e postar no Instagram via agente.

    Esta função é chamada diariamente nos horários de pico do Instagram
    (10h, 15h e 17h) para criar conteúdo otimizado e fazer a postagem.

    :param user_number: Número do usuário destinatário
    :param whatsapp_service: Instância do serviço WhatsApp
    :return: Dicionário com status da operação
    """
    try:
        logger.info('📸 Iniciando tarefa agendada: postagem no Instagram')

        # Carrega prompt do arquivo
        prompt = _load_prompt('instagram_post.md')

        # Processa com o agente
        result = await process_message_with_agent(
            user_number=user_number,
            message_text=prompt,
            whatsapp_service=whatsapp_service,
        )

        if result['status'] == 'ok':
            logger.success('✅ Postagem no Instagram realizada com sucesso')
        else:
            logger.error(
                f'❌ Falha na postagem do Instagram: {result["detail"]}'
            )

        return result

    except Exception as e:
        logger.error(f'❌ Erro na tarefa agendada do Instagram: {e}')
        logger.exception('Detalhes do erro:')
        return {'status': 'error', 'detail': str(e)}


async def trigger_linkedin_post_agent(
    user_number: str,
    whatsapp_service: WhatsAppService,
) -> dict:
    """
    Tarefa agendada para criar e postar no LinkedIn via agente.

    Esta função é chamada diariamente nos horários de pico do LinkedIn
    (8h e 14h) para criar conteúdo profissional e fazer a postagem.

    :param user_number: Número do usuário destinatário
    :param whatsapp_service: Instância do serviço WhatsApp
    :return: Dicionário com status da operação
    """
    try:
        logger.info('💼 Iniciando tarefa agendada: postagem no LinkedIn')

        # Carrega prompt do arquivo
        prompt = _load_prompt('linkedin_post.md')

        # Processa com o agente
        result = await process_message_with_agent(
            user_number=user_number,
            message_text=prompt,
            whatsapp_service=whatsapp_service,
        )

        if result['status'] == 'ok':
            logger.success('✅ Postagem no LinkedIn realizada com sucesso')
        else:
            logger.error(
                f'❌ Falha na postagem do LinkedIn: {result["detail"]}'
            )

        return result

    except Exception as e:
        logger.error(f'❌ Erro na tarefa agendada do LinkedIn: {e}')
        logger.exception('Detalhes do erro:')
        return {'status': 'error', 'detail': str(e)}


async def trigger_whatsapp_status_agent(
    user_number: str,
    whatsapp_service: WhatsAppService,
) -> dict:
    """
    Tarefa agendada para criar e postar Status no WhatsApp via agente.

    Esta função é chamada diariamente nos horários de pico do WhatsApp
    (12h, 17h e 19h) para criar conteúdo visual e postar como Status.

    :param user_number: Número do usuário destinatário
    :param whatsapp_service: Instância do serviço WhatsApp
    :return: Dicionário com status da operação
    """
    try:
        logger.info('📱 Iniciando tarefa agendada: Status do WhatsApp')

        # Carrega prompt do arquivo
        prompt = _load_prompt('whatsapp_status.md')

        # Processa com o agente
        result = await process_message_with_agent(
            user_number=user_number,
            message_text=prompt,
            whatsapp_service=whatsapp_service,
        )

        if result['status'] == 'ok':
            logger.success('✅ Status do WhatsApp postado com sucesso')
        else:
            logger.error(f'❌ Falha no Status do WhatsApp: {result["detail"]}')

        return result

    except Exception as e:
        logger.error(f'❌ Erro na tarefa agendada do WhatsApp Status: {e}')
        logger.exception('Detalhes do erro:')
        return {'status': 'error', 'detail': str(e)}
