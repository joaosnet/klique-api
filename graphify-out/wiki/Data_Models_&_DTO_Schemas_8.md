# Data Models & DTO Schemas

> 14 nodes · cohesion 0.19

## Key Concepts

- **_compute_domain_stats()** (11 connections) — `app/routers/domains.py`
- **list_domains()** (11 connections) — `app/routers/domains.py`
- **get_domain_images_collection()** (8 connections) — `app/database.py`
- **get_domain()** (7 connections) — `app/routers/domains.py`
- **Domain** (7 connections) — `app/routers/schemas.py`
- **DomainWithStats** (5 connections) — `app/routers/schemas.py`
- **DomainStats** (4 connections) — `app/routers/schemas.py`
- **get** (2 connections)
- **Collection para cache global de imagens de domínio (por tema).** (1 connections) — `app/database.py`
- **fetch_accuracy()** (1 connections) — `app/routers/domains.py`
- **fetch_due_today()** (1 connections) — `app/routers/domains.py`
- **Lista todos os domínios do usuário com suas estatísticas.** (1 connections) — `app/routers/domains.py`
- **Retorna um domínio específico com suas estatísticas.** (1 connections) — `app/routers/domains.py`
- **Calcula as estatísticas de um domínio usando consultas concorrentes.** (1 connections) — `app/routers/domains.py`

## Relationships

- [Data Models & DTO Schemas](Data_Models_&_DTO_Schemas.md) (5 shared connections)
- [Flashcards Generation & SRS](Flashcards_Generation_&_SRS.md) (3 shared connections)
- [Authentication & Tokens](Authentication_&_Tokens.md) (2 shared connections)
- [Billing & PIX Payments](Billing_&_PIX_Payments.md) (2 shared connections)

## Source Files

- `app/database.py`
- `app/routers/domains.py`
- `app/routers/schemas.py`

## Audit Trail

- EXTRACTED: 24 (83%)
- INFERRED: 5 (17%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*