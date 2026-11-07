# WhatsApp Integration Service

> 20 nodes · cohesion 0.15

## Key Concepts

- **test_status_deletion_detailed()** (11 connections) — `tests/test_status_deletion.py`
- **test_status_deletion.py** (10 connections) — `tests/test_status_deletion.py`
- **_delete_latest_status()** (6 connections) — `app/routers/whatsapp.py`
- **.get_latest_status_id()** (6 connections) — `app/services/whatsapp.py`
- **test_status_existence_check()** (6 connections) — `tests/test_status_deletion.py`
- **.delete_status()** (5 connections) — `app/services/whatsapp.py`
- **.status_exists()** (5 connections) — `app/services/whatsapp.py`
- **test_delete_nonexistent_status()** (5 connections) — `tests/test_status_deletion.py`
- **.get_status_messages()** (4 connections) — `app/services/whatsapp.py`
- **asyncio** (4 connections)
- **io** (3 connections)
- **Deleta o status mais recente. :return: True se deletou com sucesso ou não havia…** (1 connections) — `app/routers/whatsapp.py`
- **Verifica se um status ainda existe consultando as mensagens de status. :param…** (1 connections) — `app/services/whatsapp.py`
- **Deleta um status específico. :param status_id: O ID do status a ser deletado.…** (1 connections) — `app/services/whatsapp.py`
- **Busca mensagens de status do WhatsApp. :param offset: Offset para paginação.…** (1 connections) — `app/services/whatsapp.py`
- **Busca o ID do status mais recente consultando as mensagens de status. :return:…** (1 connections) — `app/services/whatsapp.py`
- **pil** (1 connections)
- **Teste para deletar um status que não existe.** (1 connections) — `tests/test_status_deletion.py`
- **Teste para verificar a existência de status.** (1 connections) — `tests/test_status_deletion.py`
- **Teste detalhado para investigar o problema de deleção de status.** (1 connections) — `tests/test_status_deletion.py`

## Relationships

- [WhatsApp Integration Service](WhatsApp_Integration_Service.md) (7 shared connections)
- [Automated Test Suite](Automated_Test_Suite.md) (2 shared connections)
- [Flashcards Generation & SRS](Flashcards_Generation_&_SRS.md) (2 shared connections)

## Source Files

- `app/routers/whatsapp.py`
- `app/services/whatsapp.py`
- `tests/test_status_deletion.py`

## Audit Trail

- EXTRACTED: 26 (67%)
- INFERRED: 13 (33%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*