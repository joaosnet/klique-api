# Flashcards Generation & SRS

> 13 nodes · cohesion 0.18

## Key Concepts

- **scheduler.py** (18 connections) — `app/scheduler.py`
- **get_reviews_collection()** (10 connections) — `app/database.py`
- **_send_srs_daily_reminder()** (8 connections) — `app/scheduler.py`
- **setup_scheduler()** (5 connections) — `app/scheduler.py`
- **get_scheduler_status()** (2 connections) — `app/scheduler.py`
- **Collection para estado de revisão SRS por card/usuário.** (1 connections) — `app/database.py`
- **Módulo de agendamento de tarefas usando APScheduler. Agenda lembretes diários…** (1 connections) — `app/scheduler.py`
- **Retorna o status atual do scheduler.** (1 connections) — `app/scheduler.py`
- **Configura as tarefas agendadas no scheduler.** (1 connections) — `app/scheduler.py`
- **Envia mensagem WhatsApp para usuários com cards vencidos hoje.** (1 connections) — `app/scheduler.py`
- **apscheduler_schedulers_asyncio** (1 connections)
- **apscheduler_triggers_cron** (1 connections)
- **zoneinfo** (1 connections)

## Relationships

- [WhatsApp Integration Service](WhatsApp_Integration_Service.md) (7 shared connections)
- [Authentication & Tokens](Authentication_&_Tokens.md) (2 shared connections)
- [Database & MongoDB Connections](Database_&_MongoDB_Connections.md) (2 shared connections)
- [Data Models & DTO Schemas](Data_Models_&_DTO_Schemas.md) (2 shared connections)
- [Billing & PIX Payments](Billing_&_PIX_Payments.md) (1 shared connections)

## Source Files

- `app/database.py`
- `app/scheduler.py`

## Audit Trail

- EXTRACTED: 25 (89%)
- INFERRED: 3 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*