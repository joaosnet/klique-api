# Tecnologias e Ferramentas

## Linguagem

*   **Python 3.12+**

## Framework Principal

*   **FastAPI**: Utilizado para construir a API web de alta performance.

## Dependências Principais

*   `fastapi[standard]`: Inclui o FastAPI e dependências recomendadas como `pydantic` para validação de dados e `uvicorn` para o servidor ASGI.
*   `google-generativeai`: A biblioteca oficial do Google para interagir com a API do Gemini (`google.genai`).
*   `pillow`: Biblioteca para manipulação e processamento de imagens.
*   `python-dotenv`: Para carregar variáveis de ambiente a partir de um arquivo `.env`.

## Ferramentas de Desenvolvimento e Testes

*   **uv**: Usado como gerenciador de pacotes e ambientes virtuais, uma alternativa rápida ao `pip` e `venv`.
*   `httpx`: Um cliente HTTP assíncrono para fazer requisições à API durante os testes.
*   `pytest`: O framework principal para a escrita e execução de testes.
*   `pytest-asyncio`: Plugin para `pytest` que permite testar código assíncrono.
*   `rich`: Usado para melhorar a visualização de logs e outras saídas no terminal com formatação rica.

## Configuração de Ambiente

As configurações da aplicação, como as credenciais da API do Gemini e timeouts, são gerenciadas através de variáveis de ambiente, conforme definido em `src/config.py`.