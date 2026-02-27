# Klique API

Plataforma fullstack para geração de avatares com IA. O produto principal é o **fotodenatal.me** — um gerador de avatares natalinos que transforma fotos de usuários em personagens de Natal usando Google Gemini. O projeto também inclui um agente de IA via WhatsApp para automação de redes sociais.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.120+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.14+-3776AB?style=flat-square&logo=python)](https://python.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://mongodb.com)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)

---

## O que é este projeto

O Klique API é composto por três partes:

1. **Backend (FastAPI)** — API REST em Python que orquestra geração de imagens, autenticação, pagamentos e o agente de IA.
2. **Frontend (React)** — SPA servida via Nginx com as páginas de landing, login, gerador de avatares, mural e painel do usuário.
3. **Dashboard** — Painel administrativo em HTML/JS puro para gestão interna.

---

## Como funciona

### Fluxo principal: Geração de avatar natalino

1. O usuário acessa o site e faz upload de uma foto.
2. O backend verifica se ele tem créditos (1 crédito grátis para novos usuários/convidados por IP; créditos pagos via PIX).
3. A foto é enviada ao **Google Gemini WebAPI** (acesso via cookies de sessão do browser) com um prompt em inglês correspondente ao template escolhido (16 templates: Papai Noel, Elfo, Grinch, Boneco de Neve, etc.).
4. A imagem retornada é processada pelo **image_cleaner** (OpenCV + Pillow) que detecta e remove a marca d'água do Gemini via template matching e inpainting.
5. Se o crédito usado era gratuito, uma marca d'água da plataforma é adicionada. Se era pago, a imagem é entregue limpa.
6. O resultado é transmitido de volta ao browser via **Server-Sent Events (SSE)** com atualizações de progresso (10% → 20% → 40% → 60% → 75% → completo).

### Autenticação

- Registro com email/senha + verificação por código de 4 dígitos enviado via Gmail SMTP.
- Login retorna JWT (HS256, validade de 30 dias).
- Google OAuth suportado (verificação do ID token via `google-auth`).
- Usuários não autenticados são tratados como convidados identificados por IP (`guest_<ip>`), recebem 1 crédito grátis e precisam criar conta para obter mais.

### Pagamentos (PIX via Mercado Pago)

1. Usuário autenticado solicita `POST /api/payments/pix/create` com o valor desejado (mínimo R$ 1,00).
2. A API chama o Mercado Pago para criar um pagamento PIX com validade de 24h e retorna o QR code e o código copia-e-cola.
3. Ao receber o pagamento, o Mercado Pago envia um webhook para `POST /api/payments/webhook`.
4. A API verifica a assinatura HMAC, confirma o status `approved` e adiciona os créditos pagos ao usuário.

### Agente de IA via WhatsApp

- Mensagens chegam via webhook do container `go-whatsapp-web-multidevice`.
- O backend deduplica mensagens e as despacha para o agente **LangGraph** com `gemini-2.5-flash`.
- O agente tem acesso a ferramentas via protocolo MCP (Obsidian, Google Drive, Instagram, LinkedIn) e mantém histórico de conversa por usuário usando `MemorySaver` com `thread_id = número_do_telefone`.
- A resposta é enviada de volta ao usuário pelo serviço HTTP do WhatsApp.

### Agendamento de redes sociais

O **APScheduler** executa tarefas automáticas no fuso horário de São Paulo:

| Horário | Tarefa |
|---------|--------|
| Diário 11:00 | Resumo do SIGAA (sistema acadêmico) |
| Ter/Qui 8:00 e 14:00 | Publicação no LinkedIn |
| Seg-Sex 10:00 | Publicação no Instagram |
| Diário | Atualização de status no WhatsApp |

Cada tarefa invoca o agente LangGraph com um prompt específico em Markdown (definido em `app/agents/prompts/`).

---

## Arquitetura

```
klique-api/
├── app/
│   ├── main.py               # Entrypoint: inicializa DB, serviços, APScheduler, monta routers
│   ├── config.py             # Todas as variáveis de ambiente e constantes
│   ├── database.py           # Cliente MongoDB assíncrono + acessores de coleções
│   ├── dependencies.py       # JWT encode/decode, hashing de senha, dependências FastAPI
│   ├── scheduler.py          # Definição dos cron jobs do APScheduler
│   ├── agents/
│   │   ├── agent.py          # Singleton LangGraph com MemorySaver + ferramentas MCP
│   │   ├── tasks.py          # Funções que invocam o agente para cada tarefa agendada
│   │   └── prompts/          # Prompts em Markdown por tarefa (Instagram, LinkedIn, etc.)
│   ├── routers/
│   │   ├── auth.py           # Login, logout, Google OAuth, troca de senha/email
│   │   ├── register.py       # Registro e verificação de email
│   │   ├── christmas.py      # Geração de avatar natalino com SSE
│   │   ├── credits.py        # Saldo, consumo e histórico de créditos
│   │   ├── payments.py       # Criação de PIX, status e webhook do Mercado Pago
│   │   ├── whatsapp.py       # Recebimento de webhook e despacho ao agente
│   │   ├── analytics.py      # Serve OG images e rastreia cliques/visualizações
│   │   ├── scheduler.py      # Endpoints HTTP para disparar tarefas manualmente
│   │   ├── telemetry.py      # Rastreamento de links com redirect e cookie
│   │   └── schemas.py        # Todos os modelos Pydantic (User, Payment, Credits...)
│   └── services/
│       ├── gemini.py         # SDK oficial do Google Gemini (imagens via WhatsApp)
│       ├── image_cleaner.py  # Remoção de marca d'água via OpenCV + inpainting
│       ├── mercadopago.py    # Integração com API do Mercado Pago
│       └── whatsapp.py       # Cliente HTTP para o container go-whatsapp
├── frontend/                 # React 19 + Vite + Tailwind CSS v4
├── dashboard/                # Painel admin em HTML/JS puro
├── scripts/
│   ├── create_admin.py       # Cria usuário admin no MongoDB via CLI
│   └── setup_cookies.py      # Extrai cookies do Gemini WebAPI do browser
├── docker-compose.yml        # Ambiente de desenvolvimento
├── docker-compose.production.yml  # Produção com Traefik + Let's Encrypt
└── Dockerfile                # Python 3.14 + uv
```

---

## Stack

| Camada | Tecnologias |
|--------|-------------|
| **Backend** | FastAPI 0.120+, Python 3.14, uv |
| **IA / Imagem** | Google Gemini WebAPI (cookies), Google Gemini SDK oficial, LangChain, LangGraph, OpenCV, Pillow |
| **Banco de dados** | MongoDB (PyMongo assíncrono) |
| **Autenticação** | JWT HS256, Argon2 (pwdlib), Google OAuth |
| **Pagamentos** | Mercado Pago PIX |
| **WhatsApp** | go-whatsapp-web-multidevice (container Docker) |
| **Scheduler** | APScheduler |
| **Agente MCP** | LangChain-MCP-Adapters via SSE |
| **Frontend** | React 19, React Router 7, Vite 7, Tailwind CSS v4 |
| **Infra** | Docker, Docker Compose, Traefik, Let's Encrypt |

---

## Coleções MongoDB

| Coleção | Conteúdo |
|---------|----------|
| `user` | Contas de usuário (email, senha Argon2, tipo) |
| `profile` | Perfil estendido (nome, cidade, avatar_url) |
| `user_credits` | Saldo de créditos gratuitos e pagos |
| `payment_transactions` | Transações PIX (pending/approved/rejected) |
| `mail_confirmation` | Códigos de verificação de email |
| `password_recovery` | Tokens de recuperação de senha |
| `processed_messages` | Deduplicação de mensagens WhatsApp |
| `link_analytics` | Rastreamento de cliques em links |

---

## Variáveis de ambiente

Copie `.env.example` para `.env` e preencha:

```bash
# JWT
SECRET_KEY=sua_chave_secreta

# Google Gemini (WebAPI via cookies — necessário para geração de avatares)
SECURE_1PSID=
SECURE_1PSIDTS=

# Google Gemini SDK oficial (necessário para o agente WhatsApp)
GOOGLE_API_KEY=

# Google OAuth
GOOGLE_CLIENT_ID=

# MongoDB
DB_HOST=localhost
DB_PORT=27017
DB_DATABASE=klique
DB_USERNAME=root
DB_PASSWORD=password

# Email (Gmail SMTP para códigos de verificação)
GMAIL_EMAIL=
GMAIL_APP_PASSWORD=

# Mercado Pago (PIX)
MP_ACCESS_TOKEN=
MP_PUBLIC_KEY=
MP_WEBHOOK_SECRET=

# Preços
FREE_CREDITS_PER_USER=1
CREDITS_PER_REAL=1
MIN_PAYMENT_AMOUNT=1.0

# Produção (Traefik)
DOMAIN=seudominio.com
ACME_EMAIL=seuemail@exemplo.com
```

> **Atenção**: `SECURE_1PSID` e `SECURE_1PSIDTS` são cookies da sessão do browser em gemini.google.com. Use `scripts/setup_cookies.py` para extrai-los automaticamente de um browser LibreWolf/Firefox.

---

## Instalação

### Desenvolvimento local

```bash
git clone https://github.com/joaosnet/klique-api.git
cd klique-api
uv sync
cp .env.example .env
# Edite .env com suas chaves
uv run task run
```

O servidor FastAPI inicia em `http://localhost:8000` com hot-reload. Documentação interativa disponível em `http://localhost:8000/docs`.

### Docker (ambiente completo)

```bash
# Sobe FastAPI + MongoDB + WhatsApp + Frontend
docker compose up -d

# Criar usuário admin
uv run task create-admin
```

### Produção

```bash
docker compose -f docker-compose.production.yml up -d
```

Requer `DOMAIN` e `ACME_EMAIL` definidos no `.env`. O Traefik gerencia HTTPS automaticamente via Let's Encrypt.

---

## Comandos úteis

```bash
uv run task run          # Inicia servidor em modo dev
uv run task test         # Executa testes (pytest)
uv run task format       # Formata código (ruff)
uv run task lint         # Verifica código (ruff)
uv run task create-admin # Cria usuário admin no MongoDB
uv run task ngrok        # Abre túnel ngrok para desenvolvimento
```

---

## Licenca

MIT License — Veja [LICENSE](./LICENSE)
