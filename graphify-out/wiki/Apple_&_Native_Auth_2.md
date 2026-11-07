# Apple & Native Auth

> 42 nodes · cohesion 0.09

## Key Concepts

- **auth.py** (81 connections) — `app/routers/auth.py`
- **post** (18 connections)
- **create_access_token()** (12 connections) — `app/dependencies.py`
- **change_password()** (8 connections) — `app/routers/auth.py`
- **login_for_access_token()** (6 connections) — `app/routers/auth.py`
- **passkey_register_verify()** (6 connections) — `app/routers/auth.py`
- **request_otp()** (6 connections) — `app/routers/auth.py`
- **verify_password()** (5 connections) — `app/dependencies.py`
- **apple_login()** (5 connections) — `app/routers/auth.py`
- **change_email()** (5 connections) — `app/routers/auth.py`
- **passkey_register_options()** (5 connections) — `app/routers/auth.py`
- **_send_email()** (5 connections) — `app/routers/auth.py`
- **confirm_change_email()** (4 connections) — `app/routers/auth.py`
- **google_login()** (4 connections) — `app/routers/auth.py`
- **logout()** (4 connections) — `app/routers/auth.py`
- **passkey_authenticate_verify()** (4 connections) — `app/routers/auth.py`
- **Depends** (4 connections)
- **request_magic_link()** (4 connections) — `app/routers/auth.py`
- **valid_token()** (4 connections) — `app/routers/auth.py`
- **verify_magic_link()** (4 connections) — `app/routers/auth.py`
- **verify_otp()** (4 connections) — `app/routers/auth.py`
- **authenticate_token()** (3 connections) — `app/dependencies.py`
- **invalidate_token()** (3 connections) — `app/dependencies.py`
- **_get_apple_public_keys()** (3 connections) — `app/routers/auth.py`
- **lazy_registration()** (3 connections) — `app/routers/auth.py`
- *... and 17 more nodes in this community*

## Relationships

- [Billing & PIX Payments](Billing_&_PIX_Payments.md) (50 shared connections)
- [Authentication & Tokens](Authentication_&_Tokens.md) (9 shared connections)
- [WhatsApp Integration Service](WhatsApp_Integration_Service.md) (5 shared connections)
- [Data Models & DTO Schemas](Data_Models_&_DTO_Schemas.md) (3 shared connections)
- [Database & MongoDB Connections](Database_&_MongoDB_Connections.md) (1 shared connections)

## Source Files

- `app/dependencies.py`
- `app/routers/auth.py`

## Audit Trail

- EXTRACTED: 127 (86%)
- INFERRED: 20 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*