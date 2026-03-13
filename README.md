# OmniFlash (Klique API)

[🇧🇷 Português](#) | [🇺🇸 English](./README.en.md) | [🇪🇸 Español](./README.es.md)

---

## 🇧🇷 OmniFlash (Klique API)

Plataforma fullstack de flashcards gamificados com elementos de **Teoria dos Jogos** e Inteligência Artificial. O OmniFlash transforma os estudos utilizando repetição espaçada (SRS) e mecânicas imersivas de análise de cenários virtuais — ideal para **concurseiros** e estudantes que buscam otimizar a memorização e a capacidade analítica através de um "Oráculo" inteligente.

[![FastAPI](https://img.shields.io/badge/FastAPI-1.0+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.10+-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://mongodb.com)
[![Docker](https://img.shields.io/badge/Docker-24.0+-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC?style=flat-square&logo=tailwind-css)](https://tailwindcss.com)

---

### 🚀 Estado Atual do Projeto

O OmniFlash evoluiu para um ecossistema completo de estudos, integrando tecnologias de ponta para oferecer uma experiência gamificada e inteligente:

1.  **Backend Moderno (FastAPI)**: API REST assíncrona robusta que gerencia domínios, deques de cartas, lógica de repetição espaçada (SRS), pagamentos e agentes de IA.
2.  **Frontend de Alta Performance (React 19)**: Interface mobile-first desenvolvida com Vite e Tailwind CSS v4, oferecendo suporte nativo a PWA e builds para Android/iOS via Capacitor.
3.  **Inteligência Artificial (Oráculo)**: Integração profunda com o Google Gemini (via Official API e WebAPI) para análise de cenários, feedbacks personalizados e mentoria virtual.
4.  **Automação e Notificações**: Sistema de agendamento de tarefas (APScheduler) e integração com WhatsApp para lembretes de estudo e interações assíncronas.
5.  **Economia Interna**: Sistema de créditos integrado com pagamentos reais via Mercado Pago (PIX).

### 📂 Estrutura de Arquivos (Filetree)

```text
klique-api/
├── app/                        # Backend (FastAPI + Python 3.12+)
│   ├── main.py                 # Ponto de entrada: inicializa DB, serviços e rotas
│   ├── config.py               # Configurações globais e variáveis de ambiente
│   ├── database.py             # Camada de conexão assíncrona com MongoDB
│   ├── scheduler.py            # Agendamento de tarefas (Retenção, Notificações)
│   ├── logger.py               # Centralização de logs estruturados
│   ├── agents/                 # Agentes inteligentes (LangGraph & MCP Tools)
│   ├── routers/                # Endpoints da API divididos por domínio
│   └── services/               # Lógica de negócio e integrações externas
├── frontend/                   # Frontend (React 19 + Vite + Tailwind v4)
│   ├── src/
│   │   ├── pages/              # Telas (Dashboard, CardSwipe, Oracle, etc.)
│   │   ├── components/         # UI Atoms, Molecules e Organisms
│   │   └── context/            # Estados globais (Auth, Theme, Multi-language)
├── scripts/                    # Scripts de automação (Create Admin, Hot Reload)
└── pyproject.toml              # Manifesto do projeto e dependências via UV
```

### ⚙️ Como Executar

O projeto utiliza o **uv** para gerenciamento ultrarrápido de dependências Python.

1.  **Backend**:
    ```bash
    uv sync
    uv run task run
    ```
2.  **Frontend**:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

---

## 📄 Licença

MIT License — Veja o arquivo [LICENSE](./LICENSE) para mais detalhes.
