"""
Módulo de criação e gerenciamento do agente LangGraph.

Este módulo implementa um agente IA com memória persistente usando LangGraph.
O agente é criado uma única vez e reutilizado entre chamadas, mantendo a
memória de conversações através do MemorySaver.

Características:
- Cache global do agente para evitar recriação
- Memória persistente entre chamadas usando MemorySaver
- Suporte a múltiplos servidores MCP (WhatsApp, Instagram, LinkedIn, etc.)
- Trimming automático de mensagens para controle de tokens
- Thread ID para isolar conversas por usuário
"""

import os
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.messages.utils import (
    count_tokens_approximately,
    trim_messages,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode
from langsmith import traceable
from loguru import logger


class AgentCache:
    _agent = None
    _checkpointer = None

    @classmethod
    async def get_agent(cls):
        """
        Cria ou retorna o agente LangGraph com memória persistente.

        Esta função implementa um padrão de singleton para o agente:
        - Na primeira chamada: cria o agente e o checkpointer
        - Nas chamadas seguintes: retorna o agente em cache

        Isso garante que:
        1. A memória do MemorySaver persiste entre chamadas
        2. Conversas são mantidas usando thread_id único por usuário
        3. O agente não precisa ser recompilado a cada mensagem

        Returns:
            CompiledGraph: Instância do agente LangGraph compilado
            com checkpointer

        Example:
            >>> agent = await AgentCache.get_agent()
            >>> response = await agent.ainvoke(
            ...     {"messages": [HumanMessage(content="Olá")]},
            ...     config={"configurable": {"thread_id": "user123"}}
            ... )
        """
        # Retorna agente em cache se já existir
        if cls._agent is not None:
            logger.debug(
                '🔄 Reutilizando agente em cache (memória preservada)'
            )
            return cls._agent

        logger.info(
            '🆕 Criando nova instância do agente com memória persistente'
        )

        # Criar checkpointer uma única vez e armazená-lo
        cls._checkpointer = MemorySaver()
        logger.info('✅ Checkpointer criado e armazenado em cache')

        checkpointer = cls._checkpointer

        # Configuração do cliente MCP para todos os servidores conectados
        # via Docker
        client = MultiServerMCPClient({
            'MCP_GATEWAY': {
                'url': 'http://host.docker.internal:8020',
                'transport': 'sse',
            },
            'sigaa-ufpa': {
                'transport': 'streamable_http',
                'url': 'http://host.docker.internal:8003/mcp',
            },
        })

        # Carregar ferramentas de todos os servidores conectados
        tools = await client.get_tools()

        # Criar o nó de ferramentas
        tool_node = ToolNode(tools)

        # llm = ChatOpenAI(
        #     api_key=GROQ_API_KEY,
        #     base_url='http://g4f:8080/api/Groq/',
        #     model='moonshotai/kimi-k2-instruct-0905',
        # )

        llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash')

        # Criar o prompt como mensagem do sistema
        system_message = open(
            os.path.join(os.path.dirname(__file__), 'system_instrutions.md'),
            'r',
            encoding='utf-8',
        ).read()

        # Bind tools to the model
        bound_model = llm.bind_tools(tools)

        # Função para determinar se deve continuar ou terminar
        def should_continue(
            state: MessagesState,
        ) -> Literal['tools', '__end__']:
            """Retorna o próximo nó a executar."""
            messages = state['messages']
            last_message = messages[-1]
            # Se não há chamadas de ferramentas, terminamos
            if not last_message.tool_calls:
                return '__end__'
            # Caso contrário, continuamos para as ferramentas
            return 'tools'

        # Definir o nó do agente
        async def call_model(state: MessagesState):
            messages = state['messages']

            # Aplicar o trimming para limitar o histórico de mensagens
            trimmed_messages = trim_messages(
                messages,
                strategy='last',
                token_counter=count_tokens_approximately,
                max_tokens=2000,
                start_on='human',
                end_on=('human', 'tool'),
            )

            # Adicionar a mensagem do sistema no início se não existir
            if not trimmed_messages or trimmed_messages[0].type != 'system':
                system_msg = SystemMessage(content=system_message)
                trimmed_messages = [system_msg] + trimmed_messages

            # Log para debug
            logger.debug(
                f'Mensagens trimmed: {len(trimmed_messages)} mensagens'
            )
            for i, msg in enumerate(trimmed_messages):
                logger.debug(f'  {i}: {msg.type} - {msg.content[:100]}...')

            # Garantir que temos pelo menos uma mensagem não-system
            non_system_messages = [
                msg for msg in trimmed_messages if msg.type != 'system'
            ]
            if not non_system_messages:
                logger.error(
                    'Nenhuma mensagem não-system encontrada após trimming!'
                )
                # Adiciona uma mensagem dummy se necessário
                trimmed_messages.append(HumanMessage(content='Olá'))

            # Invocar o modelo
            response = await bound_model.ainvoke(trimmed_messages)

            # Retornar a resposta (será adicionada às mensagens existentes)
            return {'messages': [response]}

        # Criar o grafo do estado
        workflow = StateGraph(MessagesState)

        # Adicionar os nós
        workflow.add_node('agent', call_model)
        workflow.add_node('tools', tool_node)

        # Definir o ponto de entrada
        workflow.set_entry_point('agent')

        # Adicionar edges condicionais
        workflow.add_conditional_edges(
            'agent',
            should_continue,
        )

        # Adicionar edge normal de tools para agent
        workflow.add_edge('tools', 'agent')

        # Compilar o grafo com o checkpointer
        app = workflow.compile(checkpointer=checkpointer)

        # Armazenar em cache para reutilização
        cls._agent = app
        logger.success('✅ Agente compilado e armazenado em cache')

        # Retornar o aplicativo compilado
        return app


@traceable
async def create_agent_runnable():
    """
    Cria ou retorna o agente LangGraph com memória persistente.

    Esta função implementa um padrão de singleton para o agente:
    - Na primeira chamada: cria o agente e o checkpointer
    - Nas chamadas seguintes: retorna o agente em cache

    Isso garante que:
    1. A memória do MemorySaver persiste entre chamadas
    2. Conversas são mantidas usando thread_id único por usuário
    3. O agente não precisa ser recompilado a cada mensagem

    Returns:
        CompiledGraph: Instância do agente LangGraph compilado com checkpointer

    Example:
        >>> agent = await create_agent_runnable()
        >>> response = await agent.ainvoke(
        ...     {"messages": [HumanMessage(content="Olá")]},
        ...     config={"configurable": {"thread_id": "user123"}}
        ... )
    """
    return await AgentCache.get_agent()


def reset_agent_cache() -> None:
    """
    Limpa o cache do agente, forçando a criação de uma nova instância.

    Útil para:
    - Resetar a memória completamente
    - Forçar recarregamento das ferramentas MCP
    - Debug e testes
    """
    AgentCache._agent = None
    AgentCache._checkpointer = None
    logger.info('🔄 Cache do agente resetado')
