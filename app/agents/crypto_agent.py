# Agent de Cripto usando LangChain


from langchain.agents import AgentExecutor, create_openai_tools_agent, tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from app.config import OPENROUTER_API_KEY


@tool
async def get_crypto_price(symbol: str) -> str:
    """Busca o preço de uma criptomoeda (exemplo simplificado)."""
    prices = {
        'BTC': '68,000.00 USD',
        'ETH': '3,500.00 USD',
    }
    return (
        f'O preço de {symbol.upper()} é '
        f'{prices.get(symbol.upper(), "Preço não encontrado.")}'
    )


# Defina aqui o LLM de cada agente
llm_crypto = ChatOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url='https://openrouter.ai/api/v1',
    model='openrouter/sonoma-sky-alpha',
)


def create_crypto_agent():
    tools = [get_crypto_price]
    prompt = ChatPromptTemplate.from_messages([
        (
            'system',
            'Você é um agente especialista em criptomoedas.'
            ' Use as ferramentas para responder perguntas sobre preços.',
        ),
        MessagesPlaceholder(variable_name='chat_history'),
        ('user', '{input}'),
        MessagesPlaceholder(variable_name='agent_scratchpad'),
    ])
    agent = create_openai_tools_agent(llm_crypto, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return executor
