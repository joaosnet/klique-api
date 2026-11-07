# Data Models & DTO Schemas

> 20 nodes · cohesion 0.13

## Key Concepts

- **routers/whatsapp.py** (35 connections) — `app/routers/whatsapp.py`
- **_process_message_request()** (10 connections) — `app/routers/whatsapp.py`
- **_mark_message_as_processed()** (4 connections) — `app/routers/whatsapp.py`
- **MessageProcessingData** (4 connections) — `app/routers/whatsapp.py`
- **_cleanup_old_processed_messages()** (3 connections) — `app/routers/whatsapp.py`
- **_is_message_already_processed()** (3 connections) — `app/routers/whatsapp.py`
- **_validate_message_access()** (3 connections) — `app/routers/whatsapp.py`
- **_extract_media_paths()** (2 connections) — `app/routers/whatsapp.py`
- **SessionUpdateData** (2 connections) — `app/routers/whatsapp.py`
- **_update_status_cache()** (2 connections) — `app/routers/whatsapp.py`
- **Dados para marcar mensagem como processada.** (1 connections) — `app/routers/whatsapp.py`
- **Marca uma mensagem como processada no cache.** (1 connections) — `app/routers/whatsapp.py`
- **Remove mensagens processadas com mais de 24 horas.** (1 connections) — `app/routers/whatsapp.py`
- **Dados para atualização de sessão do usuário.** (1 connections) — `app/routers/whatsapp.py`
- **Verifica se uma mensagem já foi processada anteriormente. Returns: tuple:…** (1 connections) — `app/routers/whatsapp.py`
- **Extrai caminhos de mídia do payload.** (1 connections) — `app/routers/whatsapp.py`
- **Atualiza cache de status para variações automáticas.** (1 connections) — `app/routers/whatsapp.py`
- **Valida acesso à mensagem e retorna resposta de erro se inválido.** (1 connections) — `app/routers/whatsapp.py`
- **Processa uma solicitação de mensagem.** (1 connections) — `app/routers/whatsapp.py`
- **dataclasses** (1 connections)

## Relationships

- [WhatsApp Integration Service](WhatsApp_Integration_Service.md) (16 shared connections)
- [Data Models & DTO Schemas](Data_Models_&_DTO_Schemas.md) (6 shared connections)
- [Billing & PIX Payments](Billing_&_PIX_Payments.md) (4 shared connections)
- [Authentication & Tokens](Authentication_&_Tokens.md) (1 shared connections)

## Source Files

- `app/routers/whatsapp.py`

## Audit Trail

- EXTRACTED: 51 (98%)
- INFERRED: 1 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*