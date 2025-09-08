# Tecnologias e Ferramentas

## Linguagem

*   **Python 3.12.4+**

## Framework Principal

*   **FastAPI**: Utilizado para construir a API web de alta performance.

## Dependências Principais

*   `fastapi[standard]`: Inclui o FastAPI e dependências recomendadas como `pydantic` para validação de dados e `uvicorn` para o servidor ASGI.
*   `google-genai`: A biblioteca oficial do Google para interagir com a API do Gemini (`google.genai`) - versão atual para geração de imagens.
*   `pillow`: Biblioteca para manipulação e processamento de imagens.
*   `python-dotenv`: Para carregar variáveis de ambiente a partir de um arquivo `.env`.

## Dependências de Banco de Dados e Cache

*   `motor`: Driver assíncrono para MongoDB usado com FastAPI.
*   Sistema de cache unificado MongoDB substituindo cache em memória anterior.

## Dependências de Autenticação e Segurança

*   `pwdlib[argon2]`: Biblioteca para hash de senhas com suporte ao Argon2.
*   `pyjwt`: Para trabalhar com tokens JWT.
*   `python-jose`: Biblioteca para JSON Web Signature e criptografia.

## Outras Dependências

*   `browser-cookie3`: Para trabalhar com cookies de navegador.
*   `firebase-admin`: SDK do Firebase Admin para Python.
*   `google-auth`: Biblioteca de autenticação do Google.
*   `requests`: Cliente HTTP síncrono.
*   `gemini-webapi`: API web do Gemini (mantida para compatibilidade, mas não é a implementação principal).

## Ferramentas de Desenvolvimento e Testes

*   **uv**: Usado como gerenciador de pacotes e ambientes virtuais, uma alternativa rápida ao `pip` e `venv`.
*   `httpx`: Um cliente HTTP assíncrono para fazer requisições à API durante os testes.
*   `pytest`: O framework principal para a escrita e execução de testes.
*   `pytest-asyncio`: Plugin para `pytest` que permite testar código assíncrono.
*   `rich`: Usado para melhorar a visualização de logs e outras saídas no terminal com formatação rica.
*   `ruff`: Linter e formatador de código Python moderno e rápido.
*   `taskipy`: Ferramenta para automação de tarefas definidas no `pyproject.toml`.

## Configuração de Ambiente

As configurações da aplicação, como as credenciais da API do Gemini e timeouts, são gerenciadas através de variáveis de ambiente, conforme definido em [`app/config.py`](app/config.py:1).

## Configurações de Desenvolvimento

*   **Gerenciador de Tarefas**: `taskipy` com tarefas definidas para linting, formatação, execução e testes.
*   **Formatação**: `ruff` configurado com linha máxima de 79 caracteres e aspas simples.
*   **Testes**: `pytest` configurado com modo assíncrono automático e cobertura de código.
*   **Logging**: Sistema de logging personalizado usando `loguru` com Rich para formatação.

## Serviços de Geração de Imagem

### Serviço Principal - Google GenAI Oficial
*   **Biblioteca**: `google-genai` v1.33.0+
*   **Modelo de geração**: `gemini-2.5-flash-image-preview`
*   **Modelo de enhancement**: `gemini-2.5-flash-lite`
*   **Implementação**: [`app/services/gemini.py`](app/services/gemini.py:1)
*   **Autenticação**: Via `GOOGLE_API_KEY`

### Serviço Alternativo - Gemini Web API
*   **Biblioteca**: `gemini-webapi` v1.15.0+
*   **Implementação**: [`app/services/gemini_webapi_service.py`](app/services/gemini_webapi_service.py:1)
*   **Autenticação**: Via cookies `SECURE_1PSID` e `SECURE_1PSIDTS`
*   **Funcionalidades**: Sessão persistente, geração com contexto
*   **Configuração**: Documentada em [`docs/gemini-webapi-docker-setup.md`](docs/gemini-webapi-docker-setup.md:1)

## Ambiente de Execução

### Docker Compose
*   **Serviços**: `whatsapp`, `mongodb`, `fastapi-app`
*   **Volumes**: Persistência de dados WhatsApp, MongoDB e cookies Gemini
*   **Rede**: Comunicação interna entre serviços
*   **Configuração**: [`docker-compose.yml`](docker-compose.yml:1)

### Variáveis de Ambiente Essenciais
*   `GOOGLE_API_KEY`: Chave da API oficial do Google
*   `SECURE_1PSID`, `SECURE_1PSIDTS`: Cookies para Gemini Web API
*   `DB_*`: Configurações do MongoDB
*   Configurações completas no docker-compose.yml