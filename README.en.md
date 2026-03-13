# OmniFlash (Klique API)

[🇺🇸 English](#) | [🇧🇷 Português](./README.md) | [🇪🇸 Español](./README.es.md)

---

## 🇺🇸 OmniFlash (Klique API)

Fullstack platform for gamified flashcards with **Game Theory** elements and Artificial Intelligence. OmniFlash transforms studies using Spaced Repetition (SRS) and immersive virtual scenario analysis — ideal for student and lifelong learners who seek to optimize memorization and analytical capacity through an intelligent "Oracle".

[![FastAPI](https://img.shields.io/badge/FastAPI-1.0+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.10+-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://mongodb.com)
[![Docker](https://img.shields.io/badge/Docker-24.0+-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC?style=flat-square&logo=tailwind-css)](https://tailwindcss.com)

---

### 🚀 Current Project State

OmniFlash has evolved into a complete study ecosystem, integrating cutting-edge technologies to offer a gamified and smart experience:

1.  **Modern Backend (FastAPI)**: Robust asynchronous REST API managing domains, card decks, Spaced Repetition logic (SRS), payments, and AI agents.
2.  **High-Performance Frontend (React 19)**: Mobile-first interface built with Vite and Tailwind CSS v4, offering native PWA support and Android/iOS builds via Capacitor.
3.  **Artificial Intelligence (Oracle)**: Deep integration with Google Gemini (via Official API and WebAPI) for scenario analysis, personalized feedback, and virtual mentoring.
4.  **Automation and Notifications**: Task scheduling system (APScheduler) and WhatsApp integration for study reminders and asynchronous interactions.
5.  **Internal Economy**: Credit system integrated with real payments via Mercado Pago (PIX).

### 📂 File Structure (Filetree)

```text
klique-api/
├── app/                        # Backend (FastAPI + Python 3.12+)
│   ├── main.py                 # Entry point: DB, services, and route init
│   ├── config.py               # Global settings and environment variables
│   ├── database.py             # Asynchronous MongoDB connection layer
│   ├── scheduler.py            # Task scheduling (Retention, Notifications)
│   ├── logger.py               # Structured logs centralization
│   ├── agents/                 # Intelligent Agents (LangGraph & MCP Tools)
│   ├── routers/                # API Endpoints divided by domain
│   └── services/               # Business logic and external integrations
├── frontend/                   # Frontend (React 19 + Vite + Tailwind v4)
│   ├── src/
│   │   ├── pages/              # Screens (Dashboard, CardSwipe, Oracle, etc.)
│   │   ├── components/         # UI Atoms, Molecules, and Organisms
│   │   └── context/            # Global states (Auth, Theme, Multi-language)
├── scripts/                    # Automation scripts (Create Admin, Hot Reload)
└── pyproject.toml              # Project manifesto and dependencies via UV
```

### ⚙️ How to Run

The project uses **uv** for ultra-fast Python dependency management.

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

## 📄 License

MIT License — See [LICENSE](./LICENSE) for details.
