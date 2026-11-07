# Authentication & Tokens

> 22 nodes · cohesion 0.16

## Key Concepts

- **database.py** (44 connections) — `app/database.py`
- **get_db()** (25 connections) — `app/database.py`
- **webhook_dependencies.py** (10 connections) — `app/webhook_dependencies.py`
- **get_simulation_logs_collection()** (7 connections) — `app/database.py`
- **get_link_analytics_collection()** (3 connections) — `app/database.py`
- **get_magic_links_collection()** (3 connections) — `app/database.py`
- **get_mail_confirmation_collection()** (3 connections) — `app/database.py`
- **get_otp_collection()** (3 connections) — `app/database.py`
- **get_webauthn_challenges_collection()** (3 connections) — `app/database.py`
- **get_cache_collection()** (2 connections) — `app/database.py`
- **get_password_recovery_collection()** (2 connections) — `app/database.py`
- **get_processed_messages_collection()** (2 connections) — `app/database.py`
- **get_status_generation_rate_limit_collection()** (2 connections) — `app/database.py`
- **get_status_images_collection()** (2 connections) — `app/database.py`
- **get_status_recent_viewers_collection()** (2 connections) — `app/database.py`
- **get_status_views_collection()** (2 connections) — `app/database.py`
- **get_user_sessions_collection()** (2 connections) — `app/database.py`
- **Collection para rastrear views de preview (OG) e cliques em links.** (1 connections) — `app/database.py`
- **Collection para logs de sessões de treino SRS.** (1 connections) — `app/database.py`
- **Dependências específicas para webhooks.** (1 connections) — `app/webhook_dependencies.py`
- **pymongo** (1 connections)
- **pymongo_server_api** (1 connections)

## Relationships

- [Data Models & DTO Schemas](Data_Models_&_DTO_Schemas.md) (8 shared connections)
- [Billing & PIX Payments](Billing_&_PIX_Payments.md) (5 shared connections)
- [Database & MongoDB Connections](Database_&_MongoDB_Connections.md) (3 shared connections)
- [WhatsApp Integration Service](WhatsApp_Integration_Service.md) (2 shared connections)
- [Flashcards Generation & SRS](Flashcards_Generation_&_SRS.md) (1 shared connections)

## Source Files

- `app/database.py`
- `app/webhook_dependencies.py`

## Audit Trail

- EXTRACTED: 55 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*