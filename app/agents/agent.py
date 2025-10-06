from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langsmith import traceable

# -- imports mantidos para referência futura --
# from langchain_openai import ChatOpenAI
# from app.config import OPENROUTER_API_KEY


@traceable
async def create_agent_runnable():
    # Configuração do cliente MCP
    client = MultiServerMCPClient({
        'MCP_GATEWAY': {
            'url': 'http://host.docker.internal:8020',
            'transport': 'sse',
        }
    })

    # Carregar ferramentas do servidor
    tools = await client.get_tools()

    # llm = ChatOpenAI(
    #     api_key=OPENROUTER_API_KEY,
    #     base_url='http://g4f:8080/v1',
    #     model='gpt-5-high',
    # )

    llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash')

    memory_prompt = """
## Memory Tool Usage
- Store all memory for this project in database: 'project-database-name'
- Use MCP memory tools exclusively for storing project-related information
- Begin each session by:
 1. Switching to this project's database
  2. Searching memory for data relevant to the user's prompt
"""
    system_prompt = (
        'Você é um assistente útil com acesso a ferramentas MCP.'
        ' Use as ferramentas disponíveis '
        'para responder às perguntas do usuário.'
    )

    prompt = ChatPromptTemplate.from_messages([
        (
            'system',
            system_prompt + memory_prompt,
        ),
        ('human', '{input}'),
        ('placeholder', '{agent_scratchpad}'),
    ])

    agent = create_openai_functions_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # Retornar o AgentExecutor compilado
    return agent_executor
