# WhatsApp Integration Service

> 13 nodes · cohesion 0.17

## Key Concepts

- **process_status_viewed_for_image_generation()** (13 connections) — `app/routers/whatsapp.py`
- **_generate_status_caption()** (4 connections) — `app/routers/whatsapp.py`
- **_check_rate_limit()** (3 connections) — `app/routers/whatsapp.py`
- **_format_viewers_text()** (3 connections) — `app/routers/whatsapp.py`
- **_manage_recent_viewers()** (3 connections) — `app/routers/whatsapp.py`
- **.get_contact_info()** (3 connections) — `app/services/whatsapp.py`
- **Any** (2 connections)
- **Verifica rate limit para geração de status (1 por minuto).** (1 connections) — `app/routers/whatsapp.py`
- **Gerencia lista de visualizadores recentes (últimos 2 minutos).** (1 connections) — `app/routers/whatsapp.py`
- **Formata texto de visualizadores com limite.** (1 connections) — `app/routers/whatsapp.py`
- **Gera legenda criativa ou retorna fallback.** (1 connections) — `app/routers/whatsapp.py`
- **Gera nova imagem quando alguém visualiza status.** (1 connections) — `app/routers/whatsapp.py`
- **Busca informações de um contato específico pelo número de telefone. Este método…** (1 connections) — `app/services/whatsapp.py`

## Relationships

- [WhatsApp Integration Service](WhatsApp_Integration_Service.md) (4 shared connections)

## Source Files

- `app/routers/whatsapp.py`
- `app/services/whatsapp.py`

## Audit Trail

- EXTRACTED: 14 (82%)
- INFERRED: 3 (18%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*