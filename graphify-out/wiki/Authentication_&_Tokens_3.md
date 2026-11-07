# Authentication & Tokens

> 22 nodes · cohesion 0.17

## Key Concepts

- **register.py** (35 connections) — `app/routers/register.py`
- **register()** (10 connections) — `app/routers/register.py`
- **verify_email()** (8 connections) — `app/routers/register.py`
- **get_password_hash()** (7 connections) — `app/dependencies.py`
- **UserResponse** (5 connections) — `app/routers/schemas.py`
- **UserSimplified** (5 connections) — `app/routers/schemas.py`
- **random** (5 connections)
- **confirm_code()** (4 connections) — `app/routers/register.py`
- **post** (4 connections)
- **send_confirmation_code()** (4 connections) — `app/routers/register.py`
- **confirmCodeRequest** (4 connections) — `app/routers/schemas.py`
- **confirmCodeResponse** (4 connections) — `app/routers/schemas.py`
- **RegisterResponse** (4 connections) — `app/routers/schemas.py`
- **UserCreate** (4 connections) — `app/routers/schemas.py`
- **verifyEmailRequest** (4 connections) — `app/routers/schemas.py`
- **verifyEmailResponse** (4 connections) — `app/routers/schemas.py`
- **check_account()** (3 connections) — `app/routers/register.py`
- **_send_email()** (3 connections) — `app/routers/register.py`
- **smtplib** (3 connections)
- **Resposta com dados do usuário.** (1 connections) — `app/routers/schemas.py`
- **Modelo simplificado de usuário.** (1 connections) — `app/routers/schemas.py`
- **http** (1 connections)

## Relationships

- [Billing & PIX Payments](Billing_&_PIX_Payments.md) (14 shared connections)
- [Data Models & DTO Schemas](Data_Models_&_DTO_Schemas.md) (5 shared connections)
- [Apple & Native Auth](Apple_&_Native_Auth.md) (4 shared connections)
- [Database & MongoDB Connections](Database_&_MongoDB_Connections.md) (2 shared connections)
- [Authentication & Tokens](Authentication_&_Tokens.md) (1 shared connections)

## Source Files

- `app/dependencies.py`
- `app/routers/register.py`
- `app/routers/schemas.py`

## Audit Trail

- EXTRACTED: 57 (86%)
- INFERRED: 9 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*