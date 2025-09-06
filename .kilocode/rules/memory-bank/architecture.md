# Arquitetura do Klique WhatsApp Bot

## Visão Geral

A arquitetura do Klique WhatsApp Bot é baseada em microsserviços containerizados e orquestrados pelo Docker Compose. O sistema é composto por um gateway de WhatsApp (`go-whatsapp`), uma API de backend (`fastapi-app`) que atua como orquestradora, e o banco de dados `mongodb`.

## Estrutura de Diretórios (API)

A estrutura da `fastapi-app` será adaptada para incluir a nova lógica de webhook.

```
klique-api/
├── src/
│   ├── routers/
│   │   ├── whatsapp.py  # Endpoint para receber webhooks do go-whatsapp
│   │   └── ...
│   ├── services/
│   │   ├── gemini.py    # Lógica para interagir com a API do Gemini
│   │   └── whatsapp.py  # Cliente para a API REST do go-whatsapp
│   ├── ...
├── main.py
└── ...
```

## Componentes Principais

*   **`go-whatsapp` (Gateway)**:
    *   Serviço baseado na imagem `ghcr.io/aldinokemal/go-whatsapp-web-multidevice`.
    *   Responsável por se conectar à rede do WhatsApp.
    *   Expõe uma API REST na porta `3000` para envio de mensagens e atualização de status.
    *   Envia um webhook para a `fastapi-app` a cada nova mensagem recebida.

*   **`fastapi-app` (Backend/Orquestrador)**:
    *   Recebe os webhooks do `go-whatsapp` em um endpoint dedicado (ex: `/webhooks/whatsapp`).
    *   Processa o prompt da mensagem recebida (texto e/ou imagem).
    *   Faz o download da imagem de entrada, se houver, através do `WhatsAppService`.
    *   Chama o `GeminiService` para gerar a imagem.
    *   Utiliza um cliente HTTP interno (`WhatsAppService`) para fazer chamadas à API REST do `go-whatsapp`, enviando a imagem gerada e atualizando o status.

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
```