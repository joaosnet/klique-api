# OmniFlash

Plataforma fullstack de flashcards gamificados com elementos de **Teoria dos Jogos**. O OmniFlash transforma os estudos utilizando repetição espaçada e mecânicas imersivas de análise de cenários virtuais — ideal para **concurseiros** e estudantes de qualquer área que queiram otimizar sua memorização e capacidade analítica. O projeto também inclui um agente de IA via WhatsApp para automação e lembretes de estudo.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.120+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://mongodb.com)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)

---

## O que é este projeto

O OmniFlash é composto por três partes principais:

1.  **Backend (FastAPI)** — API REST em Python que orquestra os domínios, deques de cartas, cálculo de repetição espaçada (SRS), autenticação e pagamentos.
2.  **Frontend (React)** — SPA focada na experiência mobile via PWA servida com Vite. Contém a interface gamificada de flashcards (Cards, Simulador de Teorias) e dashboards de progresso estilo "Oráculo".
3.  **Agente de IA via WhatsApp** — Sistema assíncrono para interações e lembretes de estudo.

---

## Principais Funcionalidades

### Flashcards + Teoria dos Jogos

-   **Cards Gamificados**: As cartas de estudo (flashcards) recebem classificações e um "Heat Score" probabilístico (ex: Cenários de "Black Swan", "Payoff Matrix", "If Then").
-   **Oráculo Neural**: Um modelo de IA que atua como mentor virtual ao virar a carta, fornecendo a resposta e uma análise preditiva do cenário.
-   **Domínios de Estudo**: Organização por áreas temáticas com acompanhamento de progresso. Perfeito para dividir as matérias de um edital de concurso público ou disciplinas universitárias.

### Autenticação & Economia (Créditos)

-   Registro com email/senha (verificado via Gmail SMTP) ou Google OAuth.
-   Ações avançadas no gerador de cenários e IA consomem créditos internos (integração PIX nativa via Mercado Pago).

### Infraestrutura e Produtividade

-   **APScheduler** gerencia tarefas regulares como sumarizações e postagens sociais do progresso.
-   **Agentes de Grafos**: Utiliza o *LangGraph* e *Protocolo MCP* para análise avançada de contexto em mensagens do WhatsApp.

---

## Arquitetura

```
omniflash/
├── app/
│   ├── main.py               # Entrypoint: inicializa DB, serviços, APScheduler, monta routers
│   ├── config.py             # Variáveis de ambiente e constantes
│   ├── database.py           # Cliente MongoDB assíncrono
│   ├── agents/               # Singleton LangGraph & ferramentas MCP (integração IA/WhatsApp)
│   ├── routers/
│   │   ├── auth.py           # Login, Google OAuth, etc.
│   │   ├── domains.py        # Gestão dos "Domínios" (matérias/tópicos)
│   │   ├── cards.py          # Gestão e criação de flashcards
│   │   ├── oracle_analytics.py # Dashboards preditivos
│   │   ├── srs.py            # Lógica de Espaced Repetition System
│   │   ├── payments.py       # Checkout PIX (Mercado Pago)
│   │   └── whatsapp.py       # Webhook WhatsApp
│   └── services/
│       └── gemini.py         # Google Gemini oficial para agentes
├── frontend/                 # React 19 + Vite + Tailwind CSS v4 + PWA
├── scripts/                  # Utilitários Python via `rich` (Taskipy)
├── docker-compose.yml        # Ambiente local dockerizado
└── Dockerfile                # Configuração do backend (Python 3.14 + uv)
```

---

## Como executar localmente

### Pré-requisitos
- [uv](https://github.com/astral-sh/uv) (Gerenciador de pacotes ultra-rápido para Python)
- Docker & Docker Compose
- Node.js (se quiser rodar o frontend isoladamente)

### Instalação

```bash
git clone https://github.com/joaosnet/klique-api.git
cd klique-api

# Instala as dependências Python via uv
uv sync

# Copia e configura o .env
cp .env.example .env
# [!] Edite o .env com suas credenciais do Banco, JWT, Gemini, etc.
```

### Inicialização (Dev Mode)

Para iniciar o servidor backend FastAPI com autoreload:
```bash
uv run task run
```
A API ficará disponível em `http://localhost:8000`.

Para iniciar os containers auxiliares (Banco, WhatsApp server, etc):
```bash
docker compose up -d
```

### Desenvolvimento Frontend
O frontend tem hot-reload interativo e também script customizado para dispositivos físicos via Capacitor (App Android Híbrido).

```bash
cd frontend
npm install
npm run dev
```

### Comandos úteis Backend
```bash
uv run task test         # Executa testes (pytest)
uv run task lint         # Verifica código (ruff)
uv run task create-admin # Cria usuário admin no MongoDB
```

---

## Licença

MIT License — Veja o arquivo [LICENSE](./LICENSE) para mais detalhes.
