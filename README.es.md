# OmniFlash (Klique API)

[🇪🇸 Español](#) | [🇧🇷 Português](./README.md) | [🇺🇸 English](./README.en.md)

<p align="center">
  <img src="docs/demo.gif" alt="Demostracion de OmniFlash" width="360" />
</p>

Plataforma fullstack de flashcards tácticos basada en Teoría de Juegos y Repetición Espaciada (SRS). El sistema modela escenarios de toma de decisiones para estudiantes y opositores mediante un motor de inferencia analítica y síntesis visual procedimental.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.10+-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://mongodb.com)
[![Docker](https://img.shields.io/badge/Docker-24.0+-2496ED?style=flat-square&logo=docker&logoColor=white)](https://docker.com)
[![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-v4-38B2AC?style=flat-square&logo=tailwind-css)](https://tailwindcss.com)

---

## Arquitectura del Sistema

El sistema se estructura en cinco subsistemas integrados mediante eventos asíncronos e interfaces REST:

| Subsistema | Componentes Principales | Función Técnica |
| :--- | :--- | :--- |
| **Backend REST** | FastAPI, Motor (AsyncIO), Pydantic v2 | Gestiona autenticación JWT/Passkey, dominios, tarjetas y liquidación de pagos. |
| **Motor SRS** | SuperMemo-2 (`_apply_sm2`), MongoDB | Calcula intervalos de repaso, factores de facilidad (EF) y consulta tarjetas vencidas. |
| **Agente Cognitivo** | LangGraph, `MemorySaver`, MultiServerMCP | Ejecuta razonamiento estratégico con aislamiento de contexto por usuario (`thread_id`). |
| **Síntesis Visual** | Gemini WebAPI, Async Semaphore, Pillow | Genera ilustraciones procedimentales 3D con caché en disco y base de datos. |
| **Frontend Reactivo** | React 19, Vite, Tailwind v4, Capacitor 6 | Interfaz mobile-first con gestos de swipe, analíticas y soporte PWA/Android. |

---

## Algoritmo de Repetición Espaciada (SM-2)

Los repasos implementan la formulación clásica del algoritmo SuperMemo-2 adaptada para ejecución asíncrona:

$$I(n) = \begin{cases} 1 & \text{si } q < 3 \\ 1 & \text{si } q \ge 3 \text{ y } n = 0 \\ 6 & \text{si } q \ge 3 \text{ y } n = 1 \\ \text{round}(I \times EF) & \text{si } q \ge 3 \text{ y } n \ge 2 \end{cases}$$

$$EF' = \max\left(1.3, \; EF + 0.1 - (5 - q) \times (0.08 + (5 - q) \times 0.02)\right)$$

- **Escala de Calificación ($q$)**: De 0 (fallo total) a 5 (recuerdo perfecto).
- **Factor de Facilidad ($EF$)**: Inicializado en 2.5 con un límite inferior estricto de 1.3.
- **Persistencia**: Registros históricos en `simulation_logs` y programación de repasos en `reviews`.

---

## Estructura del Repositorio

```text
klique-api/
├── app/                        # Núcleo de la API asíncrona (FastAPI + Python 3.12+)
│   ├── main.py                 # Punto de entrada, ciclo de vida (lifespan) y middlewares
│   ├── config.py               # Configuración de entorno y constantes operativas
│   ├── database.py             # Pools de conexión asíncrona MongoDB (Motor)
│   ├── scheduler.py            # Planificación de tareas en segundo plano (APScheduler)
│   ├── agents/                 # Agente LangGraph, checkpointer y cliente MultiServerMCP
│   ├── routers/                # Enrutadores API (auth, cards, srs, payments, credits, whatsapp)
│   └── services/               # Clientes de integración (Mercado Pago, WhatsApp, Gemini)
├── frontend/                   # Aplicación cliente (React 19 + Vite + Tailwind v4)
│   ├── src/pages/              # Vistas (CardSwipePage, TrainingPage, DashboardPage, DomainsPage)
│   ├── src/components/         # Componentes modulares de interfaz y renderizadores de tarjetas
│   └── src/context/            # Contextos globales de autenticación, tema e idioma
├── docs/                       # Demostraciones visuales, diagramas y activos de documentación
├── scripts/                    # Utilidades de automatización para administración y medios
└── pyproject.toml              # Definición de dependencias gestionadas mediante uv
```

---

## Instalación y Ejecución

### Requisitos Previos
- Python 3.12+ con el gestor `uv`
- Node.js 20+ y npm
- Instancia de MongoDB en ejecución (local o mediante Docker)

### 1. Backend
```bash
# Sincronizar dependencias
uv sync

# Iniciar el servidor API
uv run task run
```
La API escucha por defecto en `http://localhost:8000`. La documentación OpenAPI interactiva se encuentra en `/docs`.

### 2. Frontend
```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar el servidor de desarrollo
npm run dev
```
La interfaz web se ejecuta por defecto en `http://localhost:5173`.

---

## Documentación Arquitectónica y Grafo de Conocimiento

El repositorio incluye una base de conocimiento estructurada generada por Graphify en `graphify-out/`:
- **[Informe Arquitectónico (GRAPH_REPORT.md)](./graphify-out/GRAPH_REPORT.md)**: Métricas de acoplamiento, nodos centrales y conexiones transversales.
- **[Wiki de Ingeniería](./graphify-out/wiki/index.md)**: 122 artículos sobre módulos, incluyendo análisis de [WhatsAppService](./graphify-out/wiki/WhatsAppService.md), [Agentes de IA y Síntesis Visual](./graphify-out/wiki/AI_Agents_&_Image_Generation.md), [Repetición Espaciada SM-2](./graphify-out/wiki/SRS_Spaced_Repetition_&_Gamification.md) y [Economía y Pagos PIX](./graphify-out/wiki/Internal_Economy_&_PIX_Payments.md).
- **[Grafo Interactivo (HTML)](./graphify-out/graph.html)**: Visualizador web interactivo con 1.446 nodos y 2.882 aristas.

---

## Licencia

MIT License. Consulte el archivo [LICENSE](./LICENSE) para más detalles.
