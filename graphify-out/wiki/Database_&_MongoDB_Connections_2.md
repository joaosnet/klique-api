# Database & MongoDB Connections

> 11 nodes · cohesion 0.27

## Key Concepts

- **create_admin.py** (16 connections) — `scripts/create_admin.py`
- **get_users_collection()** (10 connections) — `app/database.py`
- **get_profiles_collection()** (9 connections) — `app/database.py`
- **_get_or_create_profile()** (9 connections) — `app/routers/profile_router.py`
- **close_db_connection()** (6 connections) — `app/database.py`
- **create_admin_interactive()** (5 connections) — `scripts/create_admin.py`
- **main()** (3 connections) — `scripts/create_admin.py`
- **Fecha a conexão com o MongoDB de forma assíncrona.** (1 connections) — `app/database.py`
- **Busca o perfil do utilizador, criando um vazio se não existir.** (1 connections) — `app/routers/profile_router.py`
- **rich_prompt** (1 connections)
- **rich_text** (1 connections)

## Relationships

- [Authentication & Tokens](Authentication_&_Tokens.md) (5 shared connections)
- [Android & Mobile Pipeline](Android_&_Mobile_Pipeline.md) (3 shared connections)
- [Billing & PIX Payments](Billing_&_PIX_Payments.md) (2 shared connections)
- [Flashcards Generation & SRS](Flashcards_Generation_&_SRS.md) (1 shared connections)
- [Setup Cookies Module](Setup_Cookies_Module.md) (1 shared connections)

## Source Files

- `app/database.py`
- `app/routers/profile_router.py`
- `scripts/create_admin.py`

## Audit Trail

- EXTRACTED: 27 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*