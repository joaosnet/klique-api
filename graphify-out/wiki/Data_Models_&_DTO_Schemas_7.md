# Data Models & DTO Schemas

> 18 nodes · cohesion 0.21

## Key Concepts

- **image_generation.py** (25 connections) — `app/services/image_generation.py`
- **generate_and_save_image()** (15 connections) — `app/services/image_generation.py`
- **improve_image_with_ai()** (13 connections) — `app/services/image_generation.py`
- **get_or_generate_domain_image()** (11 connections) — `app/services/image_generation.py`
- **get_domains_collection()** (8 connections) — `app/database.py`
- **build_domain_image_prompt()** (6 connections) — `app/services/image_generation.py`
- **init_demo_images()** (6 connections) — `app/services/image_generation.py`
- **Any** (5 connections)
- **test_prompt_builders_create_consistent_direction()** (5 connections) — `tests/test_image_generation_service.py`
- **build_avatar_image_prompt()** (4 connections) — `app/services/image_generation.py`
- **build_style_improvement_prompt()** (3 connections) — `app/services/image_generation.py`
- **_get_image_output_path()** (3 connections) — `app/services/image_generation.py`
- **_build_image_request_prompt()** (2 connections) — `app/services/image_generation.py`
- **Collection para domínios de treino do usuário.** (1 connections) — `app/database.py`
- **Usa a GeminiWeb API para gerar uma imagem. Retorna o path relativo da imagem…** (1 connections) — `app/services/image_generation.py`
- **Verifica se a imagem deste tema de domínio já existe no cache (shared db). Se…** (1 connections) — `app/services/image_generation.py`
- **Melhora uma imagem existente usando a IA. Tenta passar a imagem atual ao Gemini…** (1 connections) — `app/services/image_generation.py`
- **Gera imagens para as cartas e domínios da demonstração.** (1 connections) — `app/services/image_generation.py`

## Relationships

- [Data Models & DTO Schemas](Data_Models_&_DTO_Schemas.md) (8 shared connections)
- [Flashcards Generation & SRS](Flashcards_Generation_&_SRS.md) (3 shared connections)
- [Billing & PIX Payments](Billing_&_PIX_Payments.md) (3 shared connections)
- [Authentication & Tokens](Authentication_&_Tokens.md) (2 shared connections)

## Source Files

- `app/database.py`
- `app/services/image_generation.py`
- `tests/test_image_generation_service.py`

## Audit Trail

- EXTRACTED: 48 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*