# Data Models & DTO Schemas

> 22 nodes · cohesion 0.13

## Key Concepts

- **srs.py** (23 connections) — `app/routers/srs.py`
- **MongoBaseModel** (12 connections) — `app/routers/schemas.py`
- **ScenarioCard** (7 connections) — `app/routers/schemas.py`
- **get_due_cards()** (6 connections) — `app/routers/srs.py`
- **submit_review()** (6 connections) — `app/routers/srs.py`
- **get_srs_stats()** (5 connections) — `app/routers/srs.py`
- **Review** (4 connections) — `app/routers/schemas.py`
- **ReviewSubmitRequest** (4 connections) — `app/routers/schemas.py`
- **ReviewSubmitResponse** (4 connections) — `app/routers/schemas.py`
- **SRSStats** (4 connections) — `app/routers/schemas.py`
- **_apply_sm2()** (3 connections) — `app/routers/srs.py`
- **_calculate_streak()** (3 connections) — `app/routers/srs.py`
- **SimulationLog** (2 connections) — `app/routers/schemas.py`
- **get** (2 connections)
- **Base model para schemas que vêm do MongoDB. O MongoDB usa ObjectId como tipo…** (1 connections) — `app/routers/schemas.py`
- **post** (1 connections)
- **Motor de Repetição Espaçada Estratégico (SRS) — Algoritmo SuperMemo-2. O SM-2…** (1 connections) — `app/routers/srs.py`
- **Submete a avaliação de performance de um card (0-5) e atualiza o agendamento de…** (1 connections) — `app/routers/srs.py`
- **Retorna estatísticas gerais de treinamento do usuário.** (1 connections) — `app/routers/srs.py`
- **Conta dias consecutivos de treino até hoje.** (1 connections) — `app/routers/srs.py`
- **Aplica o algoritmo SuperMemo-2 e retorna (new_interval, new_ef, new_reps).** (1 connections) — `app/routers/srs.py`
- **Retorna os cards vencidos para revisão hoje, ordenados por data.** (1 connections) — `app/routers/srs.py`

## Relationships

- [Billing & PIX Payments](Billing_&_PIX_Payments.md) (12 shared connections)
- [Data Models & DTO Schemas](Data_Models_&_DTO_Schemas.md) (2 shared connections)
- [Authentication & Tokens](Authentication_&_Tokens.md) (2 shared connections)
- [Flashcards Generation & SRS](Flashcards_Generation_&_SRS.md) (1 shared connections)

## Source Files

- `app/routers/schemas.py`
- `app/routers/srs.py`

## Audit Trail

- EXTRACTED: 41 (87%)
- INFERRED: 6 (13%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*