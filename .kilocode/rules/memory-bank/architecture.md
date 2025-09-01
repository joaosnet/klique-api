# Arquitetura da Klique API

## Visão Geral

A API é construída usando o framework **FastAPI** e segue uma estrutura modular para separar as responsabilidades. O ponto de entrada da aplicação é o arquivo `main.py`, que inicializa a aplicação FastAPI, configura o cliente Gemini e inclui os roteadores.

## Estrutura de Diretórios

```
klique-api/
├── src/
│   ├── routers/
│   │   ├── generate.py  # Endpoints para geração de conteúdo e imagem
│   │   └── batch.py     # Endpoints para processamento em lote (futuro)
│   ├── services/
│   │   └── gemini.py    # Lógica de negócio para interagir com o Gemini
│   ├── config.py        # Configurações da aplicação (variáveis de ambiente)
│   └── logger.py        # Configuração do logger
├── tests/
│   └── test_main.py     # Testes para a API
├── main.py              # Ponto de entrada da aplicação
└── pyproject.toml       # Dependências e metadados do projeto
```

## Componentes Principais

*   **`main.py`**:
    *   Gerencia o ciclo de vida (`lifespan`) da aplicação FastAPI.
    *   Inicializa e armazena o `GeminiClient` no estado da aplicação (`app.state.gemini`).
    *   Inicializa o `GeminiService` (`app.state.gemini_service`).
    *   Gerencia um dicionário de sessões de chat (`app.state.chat_sessions`).
    *   Implementa um `asyncio.Semaphore` para limitar requisições concorrentes.

*   **`src/routers/`**:
    *   Contém os endpoints da API, organizados por funcionalidade.
    *   **`generate.py`**: Define os endpoints `/generate` e `/generate/image`. Eles recebem os dados da requisição, interagem com o `GeminiClient` ou `GeminiService` e retornam a resposta.

*   **`src/services/gemini.py`**:
    *   Abstrai a lógica de comunicação com a API do Gemini.
    *   Gerencia a criação de sessões de chat e o envio de prompts com ou sem imagens.

*   **`src/config.py`**:
    *   Carrega as configurações a partir de variáveis de ambiente, como credenciais da API e timeouts.

## Fluxo de Requisição (`/generate/image`)

O diagrama abaixo ilustra o fluxo de uma requisição para o endpoint de geração de imagem.

```mermaid
sequenceDiagram
    participant C as Cliente (App)
    participant A as API (FastAPI)
    participant S as GeminiService
    participant G as GeminiClient (API Externa)

    C->>A: POST /generate/image (prompt, imagem?, session_id?)
    A->>A: Verifica se existe session_id
    alt Sessão Existe
        A->>A: Recupera ChatSession de app.state.chat_sessions
    else Nova Sessão
        A->>S: start_chat()
        S->>G: Inicia nova sessão
        G-->>S: Retorna ChatSession
        S-->>A: Retorna ChatSession
        A->>A: Armazena nova sessão em app.state.chat_sessions
    end
    A->>S: send_message(chat, prompt, imagem)
    S->>G: Envia prompt e imagem
    G-->>S: Retorna imagem gerada e texto
    S-->>A: Retorna resposta
    A->>A: Codifica imagem para base64
    A-->>C: Retorna JSON {session_id, generated_image, response_text}