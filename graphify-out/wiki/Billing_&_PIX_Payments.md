# Billing & PIX Payments

> 49 nodes · cohesion 0.08

## Key Concepts

- **credits.py** (26 connections) — `app/routers/credits.py`
- **payments.py** (25 connections) — `app/routers/payments.py`
- **get_current_active_user()** (21 connections) — `app/dependencies.py`
- **FastAPI** (17 connections)
- **User** (16 connections) — `app/routers/schemas.py`
- **logger.py** (14 connections) — `app/logger.py`
- **config.py** (12 connections) — `app/config.py`
- **get_payment_transactions_collection()** (10 connections) — `app/database.py`
- **get_credits_history()** (9 connections) — `app/routers/credits.py`
- **create_pix_payment()** (9 connections) — `app/routers/payments.py`
- **get_payment_status()** (9 connections) — `app/routers/payments.py`
- **get_credits_balance()** (8 connections) — `app/routers/credits.py`
- **use_credit()** (8 connections) — `app/routers/credits.py`
- **models.py** (8 connections) — `app/routers/models.py`
- **get_user_credits_collection()** (7 connections) — `app/database.py`
- **get_or_create_user_credits()** (7 connections) — `app/routers/credits.py`
- **add_paid_credits()** (6 connections) — `app/routers/credits.py`
- **mercadopago_webhook()** (6 connections) — `app/routers/payments.py`
- **_process_approved_payment()** (6 connections) — `app/routers/payments.py`
- **read_users_me()** (5 connections) — `app/routers/auth.py`
- **use_one_credit()** (5 connections) — `app/routers/credits.py`
- **get_payment_config()** (4 connections) — `app/routers/payments.py`
- **check_user_has_credits()** (3 connections) — `app/routers/credits.py`
- **Depends** (3 connections)
- **get** (2 connections)
- *... and 24 more nodes in this community*

## Relationships

- [Billing & PIX Payments](Billing_&_PIX_Payments.md) (28 shared connections)
- [Data Models & DTO Schemas](Data_Models_&_DTO_Schemas.md) (4 shared connections)
- [Authentication & Tokens](Authentication_&_Tokens.md) (4 shared connections)
- [Flashcards Generation & SRS](Flashcards_Generation_&_SRS.md) (2 shared connections)
- [Setup Cookies Module](Setup_Cookies_Module.md) (1 shared connections)
- [WhatsApp Integration Service](WhatsApp_Integration_Service.md) (1 shared connections)
- [Apple & Native Auth](Apple_&_Native_Auth.md) (1 shared connections)
- [Android & Mobile Pipeline](Android_&_Mobile_Pipeline.md) (1 shared connections)

## Source Files

- `app/config.py`
- `app/database.py`
- `app/dependencies.py`
- `app/logger.py`
- `app/routers/auth.py`
- `app/routers/credits.py`
- `app/routers/models.py`
- `app/routers/payments.py`
- `app/routers/schemas.py`

## Audit Trail

- EXTRACTED: 119 (89%)
- INFERRED: 15 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*