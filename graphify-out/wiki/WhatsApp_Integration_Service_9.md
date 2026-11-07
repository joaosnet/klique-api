# WhatsApp Integration Service

> 7 nodes · cohesion 0.29

## Key Concepts

- **services/whatsapp.py** (13 connections) — `app/services/whatsapp.py`
- **AppServices** (6 connections) — `app/services/shared.py`
- **shared.py** (4 connections) — `app/services/shared.py`
- **.get_whatsapp_service()** (4 connections) — `app/services/shared.py`
- **get_whatsapp_service()** (2 connections) — `app/services/whatsapp.py`
- **Retorna a instância singleton do WhatsAppService. Cria a instância se ela ainda…** (1 connections) — `app/services/shared.py`
- **Contêiner para instâncias de serviços compartilhados na aplicação. Evita a…** (1 connections) — `app/services/shared.py`

## Relationships

- [WhatsApp Integration Service](WhatsApp_Integration_Service.md) (6 shared connections)
- [Billing & PIX Payments](Billing_&_PIX_Payments.md) (2 shared connections)
- [Flashcards Generation & SRS](Flashcards_Generation_&_SRS.md) (1 shared connections)
- [Authentication & Tokens](Authentication_&_Tokens.md) (1 shared connections)
- [Android & Mobile Pipeline](Android_&_Mobile_Pipeline.md) (1 shared connections)

## Source Files

- `app/services/shared.py`
- `app/services/whatsapp.py`

## Audit Trail

- EXTRACTED: 16 (94%)
- INFERRED: 1 (6%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*