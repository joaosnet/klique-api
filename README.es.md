# OmniFlash (Klique API)

[🇪🇸 Español](#) | [🇧🇷 Português](./README.md) | [🇺🇸 English](./README.en.md)

---

## 🇪🇸 OmniFlash (Klique API)

Plataforma fullstack de flashcards gamificados con elementos de **Teoría de Juegos** e Inteligencia Artificial. OmniFlash transforma los estudios utilizando repetición espaciada (SRS) y mecánicas inmersivas de análisis de escenarios virtuales — ideal para opositores y estudiantes que buscan optimizar su memorización y capacidad analítica a través de un "Oráculo" inteligente.

[![FastAPI](https://img.shields.io/badge/FastAPI-1.0+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.10+-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://mongodb.com)
[![Docker](https://img.shields.io/badge/Docker-24.0+-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC?style=flat-square&logo=tailwind-css)](https://tailwindcss.com)

---

### 🚀 Estado Actual del Proyecto

OmniFlash ha evolucionado hacia un ecosistema completo de estudios, integrando tecnologías de vanguardia para ofrecer una experiencia gamificada e inteligente:

1.  **Backend Moderno (FastAPI)**: API REST asíncrona robusta que gestiona dominios, mazos de cartas, lógica de repetición espaciada (SRS), pagos y agentes de IA.
2.  **Frontend de Alto Rendimiento (React 19)**: Interfaz mobile-first desarrollada con Vite y Tailwind CSS v4, con soporte nativo para PWA y builds para Android/iOS vía Capacitor.
3.  **Inteligencia Artificial (Oráculo)**: Integración profunda con Google Gemini (vía API oficial y WebAPI) para análisis de escenarios, retroalimentación personalizada y mentoría virtual.
4.  **Automatización y Notificaciones**: Sistema de programación de tareas (APScheduler) e integración con WhatsApp para recordatorios de estudio e interacciones asíncronas.
5.  **Economia Interna**: Sistema de créditos integrado con pagos reales vía Mercado Pago (PIX).

### 📂 Estructura de Archivos (Filetree)

```text
klique-api/
├── app/                        # Backend (FastAPI + Python 3.12+)
│   ├── main.py                 # Punto de entrada: inicialización de DB, servicios y rutas
│   ├── config.py               # Configuración global y variables de entorno
│   ├── database.py             # Capa de conexión asíncrona con MongoDB
│   ├── scheduler.py            # Programación de tareas (Retención, Notificaciones)
│   ├── logger.py               # Centralización de logs estructurados
│   ├── agents/                 # Agentes inteligentes (LangGraph & MCP Tools)
│   ├── routers/                # Endpoints de la API divididos por dominio
│   └── services/               # Lógica de negocio e integraciones externas
├── frontend/                   # Frontend (React 19 + Vite + Tailwind v4)
│   ├── src/
│   │   ├── pages/              # Pantallas (Dashboard, CardSwipe, Oracle, etc.)
│   │   ├── components/         # UI Atoms, Molecules y Organisms
│   │   └── context/            # Estados globales (Auth, Theme, Multi-language)
├── scripts/                    # Scripts de automação (Create Admin, Hot Reload)
└── pyproject.toml              # Manifiesto del proyecto y dependencias mediante UV
```

### ⚙️ Cómo Ejecutar

El proyecto utiliza **uv** para la gestión ultrarrápida de dependencias de Python.

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

## 📄 Licencia

Licencia MIT — Ver [LICENSE](./LICENSE) para más detalles.
