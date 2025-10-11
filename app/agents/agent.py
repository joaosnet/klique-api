from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.messages.utils import (
    count_tokens_approximately,
    trim_messages,
)
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode
from langsmith import traceable
from loguru import logger

from app.config import GROQ_API_KEY


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
    })

    # Carregar ferramentas de todos os servidores conectados
    tools = await client.get_tools()

    # Criar o nó de ferramentas
    tool_node = ToolNode(tools)

    llm = ChatOpenAI(
        api_key=GROQ_API_KEY,
        base_url='http://g4f:8080/api/Groq/',
        model='moonshotai/kimi-k2-instruct-0905',
    )

    # llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash')

    memory_prompt = """
## Memory Tool Usage
- Store all memory for this project in database: 'project-database-name'
- Use MCP memory tools exclusively for storing project-related information
- Begin each session by:
 1. Switching to this project's database
  2. Searching memory for data relevant to the user's prompt

## Long-term Memory (Neo4j)
- Use Neo4j-specific tools to store and retrieve long-term memories
- Store important user information, preferences, and context in Neo4j
- Retrieve user history and preferences when relevant to current conversation
"""

    short_term_memory_prompt = """
## Short-term Memory (In-Memory)
- Your conversation history with the user is automatically stored
  and retrieved from memory
- This includes the current conversation thread and recent interactions
- Use this context to maintain continuity in the current session
"""

    system_prompt = (
        'Você é um assistente útil com acesso a ferramentas MCP.'
        ' Use as ferramentas disponíveis '
        'para responder às perguntas do usuário.'
    )

    # Criar o prompt como mensagem do sistema
    system_message = system_prompt + memory_prompt + short_term_memory_prompt

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
