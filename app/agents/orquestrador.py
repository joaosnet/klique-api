from typing import Annotated, Literal

from langchain_core.messages import AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langsmith import traceable
from rich.traceback import install
from typing_extensions import TypedDict

from app.config import OPENROUTER_API_KEY

from .crypto_agent import create_crypto_agent
from .marketing_agent import create_marketing_agent

install(show_locals=True)


# Definição do estado do grafo
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    next: Literal['crypto', 'marketing', END]  # type: ignore
    user_context: dict  # Contexto do usuário (número de telefone, etc.)


# Nós dos agentes
async def crypto_node(state: AgentState):
    result = await create_crypto_agent().ainvoke({
        'input': state['messages'][-1].content,
        'chat_history': state['messages'],
    })
    output = result.get(
        'output', 'Desculpe, não consegui encontrar uma resposta.'
    )
    return {'messages': [AIMessage(content=output)]}


async def marketing_node(state: AgentState):
    result = await create_marketing_agent(
        user_context=state.get('user_context', {})
    ).ainvoke({
        'input': state['messages'][-1].content,
        'chat_history': state['messages'],
    })
    output = result.get(
        'output', 'Desculpe, não consegui encontrar uma resposta.'
    )
    return {'messages': [AIMessage(content=output)]}


# Nó do supervisor que decide o próximo passo
def supervisor_node(state: AgentState):
    # Se a última mensagem for uma AIMessage, a tarefa está concluída.
    if isinstance(state['messages'][-1], AIMessage):
        return {'next': END}
    llm_orquestrador = ChatOpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url='http://g4f:8080/v1',
        model='gpt-5-high',
    )
    # Caso contrário, use o LLM para rotear para o agente apropriado.
    response = llm_orquestrador.invoke(
        'Determine o próximo passo: '
        "'marketing' para Whatsapp(app de mensagens), Instagram, Facebook, Linkedin e outras redes sociais "  # noqa: E501
        "ou 'crypto' para criptomoedas, "
        'Conversa atual:\n' + state['messages'][-1].content
    )
    next_step = response.content.strip().lower()
    if 'crypto' in next_step:
        return {'next': 'crypto'}
    if 'marketing' in next_step:
        return {'next': 'marketing'}

    # Fallback para finalizar se a rota não for clara
    return {'next': END}


@traceable
def create_graph_runnable():
    # Construção do grafo
    graph = StateGraph(AgentState)
    graph.add_node('supervisor', supervisor_node)
    graph.add_node('crypto', crypto_node)
    graph.add_node('marketing', marketing_node)

    # Adicionando as arestas condicionais
    graph.add_conditional_edges(
        'supervisor',
        lambda state: state['next'],
        {'crypto': 'crypto', 'marketing': 'marketing', END: END},
    )
    graph.add_edge('crypto', 'supervisor')
    graph.add_edge('marketing', 'supervisor')

    graph.set_entry_point('supervisor')

    # Compilação do grafo e retorno
    return graph.compile()


# if __name__ == '__main__':
#     runnable = create_graph_runnable()
#     print("Digite sua solicitação (ou 'sair' para encerrar):")
#     while True:
#         entrada = input('> ')
#         if entrada.strip().lower() == 'sair':
#             break
#         # Invoca o grafo com a mensagem do usuário
#         resposta = runnable.invoke({'messages': [('user', entrada)]})
#         # A resposta final estará na última mensagem do agente
#         print('Resposta:', resposta['messages'][-1].content)
