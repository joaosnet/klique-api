# Arquitetura do Klique WhatsApp Bot

## Visão Geral

A arquitetura do Klique WhatsApp Bot é baseada em microsserviços containerizados e orquestrados pelo Docker Compose. O sistema é composto por um gateway de WhatsApp (`go-whatsapp`), uma API de backend (`fastapi-app`) que atua como orquestradora, e o banco de dados `mongodb`.

## Estrutura de Diretórios (API)

A estrutura atual da `fastapi-app` implementada com a lógica de webhook:

```
klique-api/
├── app/
│   ├── routers/
│   │   ├── whatsapp.py        # Endpoint para receber webhooks do go-whatsapp
│   │   ├── auth.py           # Autenticação e autorização
│   │   ├── register.py       # Registro de usuários
│   │   └── schemas.py        # Esquemas Pydantic
│   ├── services/
│   │   ├── gemini.py         # Serviço oficial Google GenAI (principal)
│   │   ├── gemini_webapi_service.py # Serviço alternativo Gemini Web API
│   │   ├── whatsapp.py       # Cliente para a API REST do go-whatsapp
│   │   └── shared.py         # Serviços compartilhados e lifespan
│   ├── command.py            # Sistema de comandos (imagem, legenda, refazer, editar, ajuda)
│   ├── config.py             # Configurações da aplicação
│   ├── database.py           # Conexões MongoDB
│   ├── dependencies.py       # Dependências para autenticação
│   ├── logger.py             # Sistema de logging
│   ├── main.py               # Aplicação FastAPI principal
│   ├── utils.py              # Utilitários compartilhados
│   └── webhook_dependencies.py # Dependências específicas para webhooks
├── tests/
│   ├── test_gemini.py        # Testes da integração com Gemini oficial
│   ├── test_gemini-webapi-service.py # Testes do serviço web API
│   └── ...
├── docs/
│   └── gemini-webapi-docker-setup.md # Configuração da Web API no Docker
├── logs/                     # Logs da aplicação
├── docker-compose.yml        # Orquestração dos serviços
├── Dockerfile               # Build da aplicação
├── pyproject.toml           # Configuração do projeto e dependências
└── uv.lock                  # Lock file das dependências
```

## Componentes Principais

*   **`go-whatsapp` (Gateway)**:
    *   Serviço baseado na imagem `ghcr.io/aldinokemal/go-whatsapp-web-multidevice`.
    *   Responsável por se conectar à rede do WhatsApp.
    *   Expõe uma API REST na porta `3000` para envio de mensagens e atualização de status.
    *   Envia um webhook para a `fastapi-app` a cada nova mensagem recebida.

*   **`fastapi-app` (Backend/Orquestrador)**:
    *   Recebe os webhooks do `go-whatsapp` no endpoint `/webhooks/whatsapp`.
    *   **Sistema de Comandos**: Implementa comandos específicos (`imagem`, `legenda`, `refazer`, `editar`, `ajuda`) sem processamento automático de mensagens livres.
    *   **Processamento Híbrido**: Utiliza dois serviços de geração de imagens:
        *   `GeminiService` (oficial) - Serviço principal usando `google-genai`
        *   `GeminiWebApiService` (web API) - Serviço alternativo usando `gemini-webapi`
    *   **Download de Mídia**: Faz download de imagens enviadas pelos usuários via `WhatsAppService`.
    *   **Geração Automática em Status**: Gera novas imagens automaticamente quando alguém visualiza um status.
    *   **Cache de Sessão MongoDB**: Mantém cache por usuário (último prompt, imagens geradas, IDs de status) exclusivamente no MongoDB.
    *   **Cliente WhatsApp**: Utiliza `WhatsAppService` para enviar mensagens, imagens e gerenciar status.

*   **`mongodb` (Banco de Dados)**:
    *   Armazena logs, informações de usuários e prompts.

## Fluxo de Requisição (Geração de Imagem via WhatsApp)

O diagrama abaixo ilustra o fluxo completo.

```mermaid
sequenceDiagram
    participant U as Usuário (WhatsApp)
    participant WAPP as go-whatsapp (Gateway)
    participant API as fastapi-app (Backend)
    participant GEMINI as Gemini API

    U->>WAPP: Envia mensagem com prompt (texto ou imagem com legenda)
    WAPP->>API: POST /webhooks/whatsapp (com dados da mensagem)
    
    activate API
    API->>API: Processa o prompt (e baixa a imagem, se aplicável)
    API->>GEMINI: Solicita geração de imagem (com ou sem imagem de entrada)
    GEMINI-->>API: Retorna imagem gerada
    deactivate API
    
    activate API
    API->>WAPP: Chama API REST para enviar imagem ao usuário
    WAPP-->>U: Entrega imagem no chat
    
    API->>WAPP: Chama API REST para atualizar status
    deactivate API