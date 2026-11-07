# Flashcards Generation & SRS

> 14 nodes · cohesion 0.21

## Key Concepts

- **os** (28 connections)
- **asyncio** (8 connections)
- **remove_card_image()** (5 connections) — `app/routers/cards.py`
- **pytest** (5 connections)
- **tests/test_gemini.py** (5 connections) — `tests/test_gemini.py`
- **delete_card()** (4 connections) — `app/routers/cards.py`
- **test_dl.py** (4 connections) — `app/test_dl.py`
- **app/test_gemini.py** (4 connections) — `app/test_gemini.py`
- **test_generation()** (3 connections) — `tests/test_gemini.py`
- **delete** (2 connections)
- **test_generation()** (2 connections) — `app/test_dl.py`
- **test_generation()** (2 connections) — `app/test_gemini.py`
- **Remove um card e seu registro de review.** (1 connections) — `app/routers/cards.py`
- **Remove a imagem associada ao card.** (1 connections) — `app/routers/cards.py`

## Relationships

- [Setup Cookies Module](Setup_Cookies_Module.md) (3 shared connections)
- [Data Models & DTO Schemas](Data_Models_&_DTO_Schemas.md) (2 shared connections)

## Source Files

- `app/routers/cards.py`
- `app/test_dl.py`
- `app/test_gemini.py`
- `tests/test_gemini.py`

## Audit Trail

- EXTRACTED: 22 (92%)
- INFERRED: 2 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*