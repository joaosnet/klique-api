# Data Models & DTO Schemas

> 29 nodes · cohesion 0.12

## Key Concepts

- **cards.py** (40 connections) — `app/routers/cards.py`
- **get_scenario_cards_collection()** (10 connections) — `app/database.py`
- **improve_card_image()** (9 connections) — `app/routers/cards.py`
- **get_or_generate_card_image()** (9 connections) — `app/services/image_generation.py`
- **swipe_card()** (8 connections) — `app/routers/cards.py`
- **_card_generation_stream()** (7 connections) — `app/routers/cards.py`
- **regenerate_card_image()** (7 connections) — `app/routers/cards.py`
- **generate_card_stream()** (6 connections) — `app/routers/cards.py`
- **ImageImproveRequest** (6 connections) — `app/routers/schemas.py`
- **build_card_image_prompt()** (6 connections) — `app/services/image_generation.py`
- **post** (5 connections)
- **json** (5 connections)
- **Request** (4 connections)
- **GenerateCardRequest** (4 connections) — `app/routers/schemas.py`
- **SwipeAction** (4 connections) — `app/routers/schemas.py`
- **SwipeResponse** (4 connections) — `app/routers/schemas.py`
- **generate_sse_event()** (3 connections) — `app/routers/cards.py`
- **BackgroundTasks** (3 connections)
- **stream_generator()** (2 connections) — `app/routers/cards.py`
- **_load_prompt()** (2 connections) — `app/routers/cards.py`
- **Collection para cards de cenário gerados e salvos.** (1 connections) — `app/database.py`
- **Rotas para geração e gerenciamento de Scenario Cards. O endpoint principal…** (1 connections) — `app/routers/cards.py`
- **Gera um único Scenario Card via SSE. O cliente recebe eventos 'progress',…** (1 connections) — `app/routers/cards.py`
- **Processa a decisão de swipe do usuário. - action='save': persiste o card + cria…** (1 connections) — `app/routers/cards.py`
- **Regenera a imagem de um card via IA, ignorando o cache.** (1 connections) — `app/routers/cards.py`
- *... and 4 more nodes in this community*

## Relationships

- [Data Models & DTO Schemas](Data_Models_&_DTO_Schemas.md) (13 shared connections)
- [Billing & PIX Payments](Billing_&_PIX_Payments.md) (10 shared connections)
- [Flashcards Generation & SRS](Flashcards_Generation_&_SRS.md) (6 shared connections)
- [Authentication & Tokens](Authentication_&_Tokens.md) (2 shared connections)
- [Android & Mobile Pipeline](Android_&_Mobile_Pipeline.md) (2 shared connections)

## Source Files

- `app/database.py`
- `app/routers/cards.py`
- `app/routers/schemas.py`
- `app/services/image_generation.py`

## Audit Trail

- EXTRACTED: 74 (89%)
- INFERRED: 9 (11%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*