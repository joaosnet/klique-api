# Data Models & DTO Schemas

> 12 nodes · cohesion 0.24

## Key Concepts

- **oracle_analytics.py** (18 connections) — `app/routers/oracle_analytics.py`
- **get_activity()** (4 connections) — `app/routers/oracle_analytics.py`
- **get_dashboard()** (4 connections) — `app/routers/oracle_analytics.py`
- **get_radar()** (4 connections) — `app/routers/oracle_analytics.py`
- **ActivityEntry** (4 connections) — `app/routers/schemas.py`
- **DashboardOverview** (4 connections) — `app/routers/schemas.py`
- **RadarEntry** (4 connections) — `app/routers/schemas.py`
- **get** (3 connections)
- **Rotas de Analytics do Estrategista (Dashboard do Oráculo). Fornece dados…** (1 connections) — `app/routers/oracle_analytics.py`
- **Retorna atividade de treino nos últimos 7 dias.** (1 connections) — `app/routers/oracle_analytics.py`
- **Retorna métricas de visão geral do estrategista.** (1 connections) — `app/routers/oracle_analytics.py`
- **Retorna proficiência por domínio para o gráfico radar. Accuracy = média de…** (1 connections) — `app/routers/oracle_analytics.py`

## Relationships

- [Billing & PIX Payments](Billing_&_PIX_Payments.md) (8 shared connections)
- [Data Models & DTO Schemas](Data_Models_&_DTO_Schemas.md) (2 shared connections)
- [Authentication & Tokens](Authentication_&_Tokens.md) (2 shared connections)
- [Flashcards Generation & SRS](Flashcards_Generation_&_SRS.md) (1 shared connections)

## Source Files

- `app/routers/oracle_analytics.py`
- `app/routers/schemas.py`

## Audit Trail

- EXTRACTED: 26 (90%)
- INFERRED: 3 (10%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*