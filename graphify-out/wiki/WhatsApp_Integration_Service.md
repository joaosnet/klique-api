# WhatsApp Integration Service

> 24 nodes · cohesion 0.08

## Key Concepts

- **WhatsAppService** (56 connections) — `app/services/whatsapp.py`
- **.send_message()** (4 connections) — `app/services/whatsapp.py`
- **.close()** (3 connections) — `app/services/whatsapp.py`
- **.check_user()** (2 connections) — `app/services/whatsapp.py`
- **.get_group_info()** (2 connections) — `app/services/whatsapp.py`
- **.get_random_failure_message()** (2 connections) — `app/services/whatsapp.py`
- **.get_user_info()** (2 connections) — `app/services/whatsapp.py`
- **.react_message()** (2 connections) — `app/services/whatsapp.py`
- **.remove_group_participants()** (2 connections) — `app/services/whatsapp.py`
- **.revoke_message()** (2 connections) — `app/services/whatsapp.py`
- **.send_link()** (2 connections) — `app/services/whatsapp.py`
- **Retorna uma mensagem de falha aleatória.** (1 connections) — `app/services/whatsapp.py`
- **Envia uma mensagem de texto e retorna o ID da mensagem. :param phone_number: O…** (1 connections) — `app/services/whatsapp.py`
- **Serviço para interagir com a API REST do go-whatsapp.** (1 connections) — `app/services/whatsapp.py`
- **Envia um link com preview.** (1 connections) — `app/services/whatsapp.py`
- **Reage a uma mensagem com um emoji.** (1 connections) — `app/services/whatsapp.py`
- **Verifica a existência de um usuário no WhatsApp.** (1 connections) — `app/services/whatsapp.py`
- **Obtém informações detalhadas de um grupo.** (1 connections) — `app/services/whatsapp.py`
- **Remove participantes de um grupo.** (1 connections) — `app/services/whatsapp.py`
- **Revoga uma mensagem para todos.** (1 connections) — `app/services/whatsapp.py`
- **Obtém as informações do usuário logado.** (1 connections) — `app/services/whatsapp.py`
- **Fecha a sessão do cliente HTTP.** (1 connections) — `app/services/whatsapp.py`
- **.create_group()** (1 connections) — `app/services/whatsapp.py`
- **.leave_group()** (1 connections) — `app/services/whatsapp.py`

## Relationships

- [WhatsApp Integration Service](WhatsApp_Integration_Service.md) (24 shared connections)
- [Avatar & Visual Comparisons](Avatar_&_Visual_Comparisons.md) (2 shared connections)

## Source Files

- `app/services/whatsapp.py`

## Audit Trail

- EXTRACTED: 49 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*