# Image Generation & Prompts

> 17 nodes · cohesion 0.19

## Key Concepts

- **test_image_generation_service.py** (12 connections) — `tests/test_image_generation_service.py`
- **FakeGeminiClient** (7 connections) — `tests/test_image_generation_service.py`
- **FakeGeneratedImage** (5 connections) — `tests/test_image_generation_service.py`
- **test_generate_and_save_image_uses_existing_source_image_for_edit()** (5 connections) — `tests/test_image_generation_service.py`
- **test_generate_and_save_image_uses_first_image_when_no_generated_image()** (5 connections) — `tests/test_image_generation_service.py`
- **test_generate_and_save_image_uses_generated_image_save()** (5 connections) — `tests/test_image_generation_service.py`
- **FakeWebImage** (4 connections) — `tests/test_image_generation_service.py`
- **asyncio** (4 connections)
- **test_generate_and_save_image_returns_cached_path_without_calling_client()** (4 connections) — `tests/test_image_generation_service.py`
- **services/__init__.py** (1 connections) — `app/services/__init__.py`
- **.generate_content()** (1 connections) — `tests/test_image_generation_service.py`
- **.__init__()** (1 connections) — `tests/test_image_generation_service.py`
- **.__init__()** (1 connections) — `tests/test_image_generation_service.py`
- **.save()** (1 connections) — `tests/test_image_generation_service.py`
- **.__init__()** (1 connections) — `tests/test_image_generation_service.py`
- **.save()** (1 connections) — `tests/test_image_generation_service.py`
- **types** (1 connections)

## Relationships

- [Data Models & DTO Schemas](Data_Models_&_DTO_Schemas.md) (6 shared connections)
- [Flashcards Generation & SRS](Flashcards_Generation_&_SRS.md) (1 shared connections)

## Source Files

- `app/services/__init__.py`
- `tests/test_image_generation_service.py`

## Audit Trail

- EXTRACTED: 33 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*