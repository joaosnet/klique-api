# WhatsApp Integration Service

> 13 nodes · cohesion 0.18

## Key Concepts

- **tasks.py** (10 connections) — `app/agents/tasks.py`
- **.get_agent()** (6 connections) — `app/agents/agent.py`
- **process_message_with_agent()** (6 connections) — `app/agents/tasks.py`
- **loguru** (5 connections)
- **AgentCache** (4 connections) — `app/agents/agent.py`
- **Instagram Post Prompt** (2 connections) — `app/agents/prompts/instagram_post.md`
- **call_model()** (1 connections) — `app/agents/agent.py`
- **should_continue()** (1 connections) — `app/agents/agent.py`
- **Cria ou retorna o agente LangGraph com memória persistente. Esta função…** (1 connections) — `app/agents/agent.py`
- **LinkedIn Post Prompt** (1 connections) — `app/agents/prompts/linkedin_post.md`
- **WhatsApp Status Prompt** (1 connections) — `app/agents/prompts/whatsapp_status.md`
- **Processa uma mensagem usando o agente LangGraph e envia a resposta via WhatsApp.** (1 connections) — `app/agents/tasks.py`
- **Google Gemini** (1 connections) — `README.en.md`

## Relationships

- [Data Models & DTO Schemas](Data_Models_&_DTO_Schemas.md) (1 shared connections)
- [AI Oracle & Intelligent Agents](AI_Oracle_&_Intelligent_Agents.md) (1 shared connections)

## Source Files

- `README.en.md`
- `app/agents/agent.py`
- `app/agents/prompts/instagram_post.md`
- `app/agents/prompts/linkedin_post.md`
- `app/agents/prompts/whatsapp_status.md`
- `app/agents/tasks.py`

## Audit Trail

- EXTRACTED: 12 (75%)
- INFERRED: 4 (25%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*