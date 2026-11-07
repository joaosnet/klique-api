# Billing & PIX Payments

> 22 nodes · cohesion 0.11

## Key Concepts

- **dependencies.py** (34 connections) — `app/dependencies.py`
- **datetime** (15 connections)
- **typing** (12 connections)
- **mercadopago.py** (11 connections) — `app/services/mercadopago.py`
- **authenticate_user()** (5 connections) — `app/dependencies.py`
- **get_current_user()** (5 connections) — `app/dependencies.py`
- **get_current_user_optional()** (5 connections) — `app/dependencies.py`
- **get_token_from_header()** (3 connections) — `app/dependencies.py`
- **Collection** (3 connections)
- **httpx** (3 connections)
- **Depends** (2 connections)
- **fastapi_security** (2 connections)
- **Header** (2 connections)
- **uuid** (2 connections)
- **Obtém o usuário atual se o token for válido, senão retorna None. Não levanta…** (1 connections) — `app/dependencies.py`
- **Serviço de integração com Mercado Pago para pagamentos PIX.** (1 connections) — `app/services/mercadopago.py`
- **hashlib** (1 connections)
- **hmac** (1 connections)
- **jose** (1 connections)
- **oauth2_scheme** (1 connections)
- **pwdlib** (1 connections)
- **pymongo_collection** (1 connections)

## Relationships

- [Billing & PIX Payments](Billing_&_PIX_Payments.md) (7 shared connections)
- [Apple & Native Auth](Apple_&_Native_Auth.md) (5 shared connections)
- [Authentication & Tokens](Authentication_&_Tokens.md) (2 shared connections)
- [Flashcards Generation & SRS](Flashcards_Generation_&_SRS.md) (1 shared connections)
- [Database & MongoDB Connections](Database_&_MongoDB_Connections.md) (1 shared connections)
- [Data Models & DTO Schemas](Data_Models_&_DTO_Schemas.md) (1 shared connections)

## Source Files

- `app/dependencies.py`
- `app/services/mercadopago.py`

## Audit Trail

- EXTRACTED: 42 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*