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


@traceable
async def create_agent_runnable():
    checkpointer = MemorySaver()

    # Configuração do cliente MCP para todos os servidores conectados
    # via Docker
    client = MultiServerMCPClient({
        'MCP_GATEWAY': {
            'url': 'http://host.docker.internal:8020',
            'transport': 'sse',
        },
        'sigaa-ufpa': {
            'transport': 'http',
            'url': 'http://host.docker.internal:8000/mcp',
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
        encoding='utf-8'
    ).read()

    # Bind tools to the model
    bound_model = llm.bind_tools(tools)

    # Função para determinar se deve continuar ou terminar
    def should_continue(state: MessagesState) -> Literal['tools', '__end__']:
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
        logger.debug(f'Mensagens trimmed: {len(trimmed_messages)} mensagens')
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

    # Retornar o aplicativo compilado
    return app
