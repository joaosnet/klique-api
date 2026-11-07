# WhatsApp Integration Service

> 8 nodes · cohesion 0.29

## Key Concepts

- **extract_user_number()** (6 connections) — `app/utils.py`
- **process_status_view()** (5 connections) — `app/routers/whatsapp.py`
- **extract_primary_user_number()** (5 connections) — `app/utils.py`
- **utils.py** (4 connections) — `app/utils.py`
- **Processa e salva visualização de status no banco.** (1 connections) — `app/routers/whatsapp.py`
- **Utilitários compartilhados da aplicação.** (1 connections) — `app/utils.py`
- **Extrai o número de telefone principal a partir de um payload de webhook. Ordem…** (1 connections) — `app/utils.py`
- **Extrai o número limpo (sem sufixos) de um sender_id. Args: sender_id: O ID do…** (1 connections) — `app/utils.py`

## Relationships

- [Billing & PIX Payments](Billing_&_PIX_Payments.md) (1 shared connections)

## Source Files

- `app/routers/whatsapp.py`
- `app/utils.py`

## Audit Trail

- EXTRACTED: 9 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*