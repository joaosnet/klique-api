# Data Models & DTO Schemas

> 14 nodes · cohesion 0.16

## Key Concepts

- **receive_whatsapp_webhook()** (9 connections) — `app/routers/whatsapp.py`
- **WebhookDependencies** (9 connections) — `app/webhook_dependencies.py`
- **_handle_status_view()** (7 connections) — `app/routers/whatsapp.py`
- **get_webhook_dependencies()** (5 connections) — `app/webhook_dependencies.py`
- **.__init__()** (3 connections) — `app/webhook_dependencies.py`
- **BackgroundTasks** (2 connections)
- **post** (1 connections)
- **Request** (1 connections)
- **Trata eventos de visualização de status.** (1 connections) — `app/routers/whatsapp.py`
- **Recebe webhooks do go-whatsapp e processa comandos/eventos.** (1 connections) — `app/routers/whatsapp.py`
- **Any** (1 connections)
- **Request** (1 connections)
- **Classe para agrupar as dependências do webhook.** (1 connections) — `app/webhook_dependencies.py`
- **Função de dependência para o webhook.** (1 connections) — `app/webhook_dependencies.py`

## Relationships

- [WhatsApp Integration Service](WhatsApp_Integration_Service.md) (5 shared connections)
- [Data Models & DTO Schemas](Data_Models_&_DTO_Schemas.md) (1 shared connections)

## Source Files

- `app/routers/whatsapp.py`
- `app/webhook_dependencies.py`

## Audit Trail

- EXTRACTED: 16 (76%)
- INFERRED: 5 (24%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*