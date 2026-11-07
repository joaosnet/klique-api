# Data Models & DTO Schemas

> 21 nodes · cohesion 0.11

## Key Concepts

- **main.py** (33 connections) — `app/main.py`
- **lifespan()** (8 connections) — `app/main.py`
- **get_client()** (6 connections) — `app/database.py`
- **get_mongodb_url()** (4 connections) — `app/config.py`
- **start_scheduler()** (4 connections) — `app/scheduler.py`
- **stop_scheduler()** (4 connections) — `app/scheduler.py`
- **add_security_headers()** (3 connections) — `app/main.py`
- **routers/__init__.py** (2 connections) — `app/routers/__init__.py`
- **Constructs the MongoDB connection URL from environment variables.** (1 connections) — `app/config.py`
- **Request** (1 connections)
- **Gerenciador de ciclo de vida do FastAPI para inicializar e encerrar os serviços…** (1 connections) — `app/main.py`
- **Inicia o scheduler de tarefas agendadas.** (1 connections) — `app/scheduler.py`
- **Para o scheduler de tarefas agendadas.** (1 connections) — `app/scheduler.py`
- **AsyncMongoClient** (1 connections)
- **contextlib** (1 connections)
- **fastapi_middleware_cors** (1 connections)
- **fastapi_middleware_gzip** (1 connections)
- **fastapi_staticfiles** (1 connections)
- **middleware** (1 connections)
- **uvicorn** (1 connections)
- **warnings** (1 connections)

## Relationships

- [Billing & PIX Payments](Billing_&_PIX_Payments.md) (7 shared connections)
- [Data Models & DTO Schemas](Data_Models_&_DTO_Schemas.md) (5 shared connections)
- [Flashcards Generation & SRS](Flashcards_Generation_&_SRS.md) (4 shared connections)
- [Authentication & Tokens](Authentication_&_Tokens.md) (2 shared connections)
- [Database & MongoDB Connections](Database_&_MongoDB_Connections.md) (2 shared connections)
- [Setup Cookies Module](Setup_Cookies_Module.md) (1 shared connections)
- [Automated Test Suite](Automated_Test_Suite.md) (1 shared connections)
- [Apple & Native Auth](Apple_&_Native_Auth.md) (1 shared connections)

## Source Files

- `app/config.py`
- `app/database.py`
- `app/main.py`
- `app/routers/__init__.py`
- `app/scheduler.py`

## Audit Trail

- EXTRACTED: 46 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*