from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_mcp_adapters.client import MultiServerMCPClient

# from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import traceable

from app.config import OPENROUTER_API_KEY


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
    try:
        tools = await client.get_tools()
        if not tools:
            print('Aviso: Nenhuma ferramenta MCP encontrada.')
            tools = []  # ou talvez retornar um agente sem ferramentas
        else:
            print(
                f'Ferramentas MCP carregadas: {[tool.name for tool in tools]}'
            )
    except Exception as e:
        print(f'Erro ao obter ferramentas MCP: {e}')
        tools = []  # ou talvez lançar uma exceção ou retornar um agente sem ferramentas
        # Neste caso, vamos prosseguir com tools=[] para ver se o erro é realmente na obtenção de ferramentas

    # Criar um agente LangChain com as ferramentas MCP
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
    print(f'Agente criado com {len(tools) if tools else 0} ferramentas.')
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    print(f'Executor criado com {len(tools) if tools else 0} ferramentas.')

    # Retornar o AgentExecutor compilado
    return agent_executor
