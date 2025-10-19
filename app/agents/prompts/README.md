# 📅 Agendador de Postagens nas Redes Sociais

## 📊 Resumo da Implementação

Este documento descreve o sistema de agendamento automático de postagens nas redes sociais implementado na Klique API, baseado em pesquisas sobre os melhores horários de engajamento em 2025.

## 🎯 Plataformas Configuradas

### 1. 💼 LinkedIn

**Dias de Postagem:** Terça, Quarta e Quinta-feira (melhores dias de engajamento)

**Horários:**
- **08:00** - Postagem matinal (início do expediente)
  - Job ID: `linkedin_morning_post`
  - Público está conferindo atualizações no início do dia
  
- **14:00** - Postagem vespertina (meio da tarde)
  - Job ID: `linkedin_afternoon_post`
  - Momento estratégico para conteúdo aprofundado

**Função:** `trigger_linkedin_post_agent()`
- Cria conteúdo profissional e relevante
- Suporta posts de texto ou com imagem do Google Drive
- Conteúdo apropriado para público profissional

---

### 2. 📸 Instagram

**Dias de Postagem:** Segunda a Sexta-feira

**Horários:**
- **10:00** - Postagem matinal (segunda a sexta)
  - Job ID: `instagram_morning_post`
  - Período de alta atividade matinal
  
- **15:00** - Postagem vespertina (segunda a sexta) **[HORÁRIO DE PICO]**
  - Job ID: `instagram_afternoon_post`
  - Principal horário de engajamento do dia
  
- **17:00** - Postagem noturna (segunda a quinta) **[HORÁRIO NOBRE]**
  - Job ID: `instagram_evening_post`
  - Usuários retornando para casa, alto engajamento

**Função:** `trigger_instagram_post_agent()`
- Seleciona imagens do Google Drive
- Cria legendas criativas
- Adiciona hashtags apropriadas
- Posta no feed do Instagram

---

### 3. 📱 WhatsApp Status

**Dias de Postagem:** Todos os dias

**Horários:**
- **12:00** - Status do meio-dia (horário de almoço)
  - Job ID: `whatsapp_status_lunch`
  - 25% mais interações durante a pausa do almoço
  
- **17:00** - Status da tarde (retorno para casa)
  - Job ID: `whatsapp_status_evening`
  - Período estratégico de transição
  
- **19:00** - Status da noite **[PICO DE ENGAJAMENTO]**
  - Job ID: `whatsapp_status_night`
  - 40% mais engajamento neste horário

**Função:** `trigger_whatsapp_status_agent()`
- Seleciona imagens do Google Drive
- Cria legendas atrativas
- Posta como Status no WhatsApp

---

## 🏗️ Arquitetura da Solução

### Arquivos Modificados

1. **`app/agents/tasks.py`**
   - ✅ `trigger_instagram_post_agent()` - Task para Instagram
   - ✅ `trigger_linkedin_post_agent()` - Task para LinkedIn
   - ✅ `trigger_whatsapp_status_agent()` - Task para WhatsApp Status
   - ✅ `_load_prompt()` - Função helper para carregar prompts de arquivos .md

2. **`app/agents/prompts/`** - Diretório com prompts em arquivos Markdown
   - ✅ `instagram_post.md` - Instruções para postagem no Instagram
   - ✅ `linkedin_post.md` - Instruções para postagem no LinkedIn
   - ✅ `whatsapp_status.md` - Instruções para Status do WhatsApp
   - ✅ `sigaa_summary.md` - Instruções para resumo do SIGAA

3. **`app/scheduler.py`**
   - ✅ Configuração de 9 jobs agendados
   - ✅ Funções auxiliares para cada horário
   - ✅ Tratamento de erros e logging detalhado

### Como Funciona

```
┌─────────────────────────────────────────────────────────────┐
│                    APScheduler (AsyncIO)                     │
│                    Timezone: America/Sao_Paulo               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      CronTriggers                            │
│  • LinkedIn: ter-qui às 8h e 14h                            │
│  • Instagram: seg-sex às 10h, 15h e 17h                     │
│  • WhatsApp: todos os dias às 12h, 17h e 19h                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Funções Auxiliares                         │
│  _post_linkedin_morning()      _post_instagram_morning()     │
│  _post_linkedin_afternoon()    _post_instagram_afternoon()   │
│                                _post_instagram_evening()      │
│  _post_whatsapp_status_lunch()                               │
│  _post_whatsapp_status_evening()                             │
│  _post_whatsapp_status_night()                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Triggers de Tasks do Agente                     │
│  • trigger_linkedin_post_agent()                             │
│  • trigger_instagram_post_agent()                            │
│  • trigger_whatsapp_status_agent()                           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   _load_prompt()                             │
│  Carrega instruções de arquivos .md:                         │
│  • app/agents/prompts/instagram_post.md                      │
│  • app/agents/prompts/linkedin_post.md                       │
│  • app/agents/prompts/whatsapp_status.md                     │
│  • app/agents/prompts/sigaa_summary.md                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│            process_message_with_agent()                      │
│  • Envia prompt ao agente IA                                 │
│  • Agente usa ferramentas MCP para:                          │
│    - Listar arquivos do Google Drive                         │
│    - Criar legendas e conteúdo                               │
│    - Fazer postagens nas plataformas                         │
│  • Notifica usuário via WhatsApp sobre status                │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Configuração de Jobs

### Parâmetros Comuns
- `replace_existing=True` - Substitui job se já existir
- `max_instances=1` - Apenas uma instância rodando por vez
- `coalesce=True` - Agrupa execuções atrasadas
- `misfire_grace_time=300` - Tolera até 5 minutos de atraso

### Tabela de Horários

| Plataforma | Job ID | Dias | Horário | Propósito |
|------------|--------|------|---------|-----------|
| LinkedIn | `linkedin_morning_post` | Ter-Qui | 08:00 | Início do expediente |
| LinkedIn | `linkedin_afternoon_post` | Ter-Qui | 14:00 | Meio da tarde |
| Instagram | `instagram_morning_post` | Seg-Sex | 10:00 | Atividade matinal |
| Instagram | `instagram_afternoon_post` | Seg-Sex | 15:00 | 🔥 Pico de engajamento |
| Instagram | `instagram_evening_post` | Seg-Qui | 17:00 | Horário nobre |
| WhatsApp | `whatsapp_status_lunch` | Todos | 12:00 | Horário de almoço |
| WhatsApp | `whatsapp_status_evening` | Todos | 17:00 | Retorno para casa |
| WhatsApp | `whatsapp_status_night` | Todos | 19:00 | 🔥 Pico de engajamento |
| SIGAA | `daily_sigaa_summary` | Todos | 11:00 | Resumo diário (legado) |

---

## 🚀 Como Usar

### 1. Verificar Status dos Jobs

```bash
GET /scheduler/status
```

Retorna informações detalhadas de todos os jobs agendados:
- Próxima execução
- Tempo restante
- Status (running/pendente)

### 2. Logs

Os logs incluem emojis para fácil identificação:
- 💼 LinkedIn
- 📸 Instagram  
- 📱 WhatsApp
- ✅ Sucesso
- ❌ Erro

Exemplo:
```
💼 [19/10/2025 08:00:00] Executando postagem matinal no LinkedIn
✅ Postagem matinal no LinkedIn realizada
```

### 3. Notificações

Todas as execuções notificam o usuário configurado via WhatsApp, incluindo:
- Status de início
- Progresso da execução
- Resultado final (sucesso/erro)

---

## 🔧 Variáveis de Ambiente

```env
SCHEDULED_TASKS_USER_NUMBER=5511999999999
```

Número do WhatsApp que receberá notificações das tarefas agendadas.

---

## 📊 Métricas e Otimização

### Horários Baseados em Dados de 2025

Os horários foram escolhidos com base em:
- Análise de milhões de interações
- Comportamento do público brasileiro
- Picos de engajamento por plataforma
- Estudos de empresas especializadas (Sprout Social, Hootsuite, etc.)

### Distribuição Semanal

```
Segunda   : IG 10h, IG 15h, IG 17h, WA 12h/17h/19h
Terça     : LI 8h, LI 14h, IG 10h, IG 15h, IG 17h, WA 12h/17h/19h
Quarta    : LI 8h, LI 14h, IG 10h, IG 15h, IG 17h, WA 12h/17h/19h
Quinta    : LI 8h, LI 14h, IG 10h, IG 15h, IG 17h, WA 12h/17h/19h
Sexta     : IG 10h, IG 15h, WA 12h/17h/19h
Sábado    : WA 12h/17h/19h
Domingo   : WA 12h/17h/19h

Total: 41 postagens por semana
```

---

## 🎨 Integração com MCP (Model Context Protocol)

O agente IA tem acesso às seguintes ferramentas via MCP:

### Google Drive
- `list_drive_files` - Lista arquivos disponíveis
- `list_drive_images` - Lista apenas imagens

### Instagram
- `upload_photo` - Posta foto no feed
- `upload_story_photo` - Posta foto como story
- `upload_story_video` - Posta vídeo como story

### LinkedIn
- `create_text_post` - Post de texto
- `create_image_post` - Post com imagem
- `create_video_post` - Post com vídeo
- `get_my_profile` - Obtém URN do perfil

### WhatsApp
- `post_status` - Posta status com imagem

---

## 🐛 Troubleshooting

### Job não está executando
1. Verifique se o scheduler está rodando: `GET /scheduler/status`
2. Confira os logs para erros
3. Verifique o timezone (deve ser `America/Sao_Paulo`)

### Postagem falhou
1. Verifique se há imagens no Google Drive
2. Confirme credenciais das redes sociais
3. Verifique logs do agente para detalhes do erro

### Horário incorreto
1. Confirme timezone do servidor
2. APScheduler usa `America/Sao_Paulo` por padrão
3. Use `get_current_time()` para verificar horário atual

---

## 📚 Referências

Baseado em pesquisas de:
- Sprout Social (2025)
- Hootsuite Blog (2025)
- RD Station (2025)
- Neil Patel (2025)
- Amper Marketing (2025)

---

## 🔮 Próximas Melhorias

- [ ] Análise de performance por horário
- [ ] A/B testing de legendas
- [ ] Ajuste dinâmico de horários baseado em métricas
- [ ] Integração com analytics das plataformas
- [ ] Suporte a agendamento de Stories do Instagram
- [ ] Diversificação de conteúdo por horário
- [ ] Sistema de aprovação antes da postagem

---

**Desenvolvido com ❤️ para maximizar engajamento nas redes sociais**


# 📝 Guia de Prompts do Agente IA

Este diretório contém todos os prompts utilizados pelo agente IA para executar tarefas automatizadas.

## 📂 Estrutura

```
app/agents/prompts/
├── __init__.py
├── instagram_post.md      # Instruções para postagens no Instagram
├── linkedin_post.md       # Instruções para postagens no LinkedIn
├── whatsapp_status.md     # Instruções para Status do WhatsApp
└── sigaa_summary.md       # Instruções para resumo do SIGAA
```

## 🎯 Como Funciona

### Carregamento de Prompts

Os prompts são carregados dinamicamente em tempo de execução pela função `_load_prompt()` em `tasks.py`:

```python
from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / 'prompts'

def _load_prompt(filename: str) -> str:
    """Carrega um prompt de um arquivo Markdown."""
    prompt_path = PROMPTS_DIR / filename
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read().strip()
```

### Uso nas Tasks

```python
async def trigger_instagram_post_agent(...):
    # Carrega prompt do arquivo
    prompt = _load_prompt('instagram_post.md')
    
    # Processa com o agente
    result = await process_message_with_agent(
        user_number=user_number,
        message_text=prompt,
        whatsapp_service=whatsapp_service,
    )
```

## 📋 Prompts Disponíveis

### 1. Instagram (`instagram_post.md`)

**Usado em:** `trigger_instagram_post_agent()`  
**Horários:** 10h, 15h, 17h (seg-qui)  
**Objetivo:** Criar e postar imagens no feed do Instagram

**Conteúdo:**
- Instruções para seleção de imagens do Google Drive
- Diretrizes para criação de legendas criativas
- Orientações sobre uso de hashtags
- Dicas de engajamento

### 2. LinkedIn (`linkedin_post.md`)

**Usado em:** `trigger_linkedin_post_agent()`  
**Horários:** 8h, 14h (ter-qui)  
**Objetivo:** Criar posts profissionais no LinkedIn

**Conteúdo:**
- Formatação de posts de texto vs. imagem
- Tom profissional mas humanizado
- Sugestões de temas corporativos
- Estrutura de gancho + desenvolvimento + CTA

### 3. WhatsApp Status (`whatsapp_status.md`)

**Usado em:** `trigger_whatsapp_status_agent()`  
**Horários:** 12h, 17h, 19h (todos os dias)  
**Objetivo:** Criar Status efêmeros no WhatsApp

**Conteúdo:**
- Características de conteúdo efêmero (24h)
- Legendas curtas e impactantes
- Temas por horário (manhã/tarde/noite)
- Tom casual e amigável

### 4. SIGAA Summary (`sigaa_summary.md`)

**Usado em:** `trigger_sigaa_summary_agent()`  
**Horários:** 11h (todos os dias)  
**Objetivo:** Resumir avisos acadêmicos

**Conteúdo:**
- Estrutura de resumo organizado
- Priorização por urgência
- Formatação clara com emojis
- Destaque de prazos importantes

## ✏️ Como Editar Prompts

### Princípios

1. **Clareza:** Instruções diretas e objetivas
2. **Contexto:** Forneça contexto suficiente para o agente
3. **Exemplos:** Inclua exemplos quando necessário
4. **Estrutura:** Use Markdown para organização visual

### Estrutura Recomendada

```markdown
# Prompt: [Nome da Task]

[Descrição breve do objetivo]

## Instruções

1. [Passo a passo do que deve ser feito]
2. ...

## Formato

[Como o conteúdo deve ser estruturado]

## Dicas

- [Orientações adicionais]
- ...

## Temas Sugeridos

- [Ideias de conteúdo]
- ...
```

### Boas Práticas

#### ✅ Faça

- Use listas numeradas para passos sequenciais
- Inclua exemplos concretos
- Especifique tom e estilo desejados
- Forneça variações por contexto (horário, dia)
- Use emojis para facilitar leitura

#### ❌ Evite

- Prompts muito genéricos
- Instruções ambíguas
- Excesso de informação
- Jargões técnicos desnecessários
- Prompts muito longos (> 500 linhas)

## 🔧 Criando Novos Prompts

### 1. Criar o arquivo

```bash
# Navegue até o diretório de prompts
cd app/agents/prompts/

# Crie um novo arquivo .md
touch nova_task.md
```

### 2. Estruturar o prompt

```markdown
# Prompt: Nova Task

Descrição clara do que o agente deve fazer.

## Instruções

1. Primeiro passo
2. Segundo passo
...

## Formato

Estrutura esperada do output.

## Observações

Pontos de atenção adicionais.
```

### 3. Criar a função de task

Em `app/agents/tasks.py`:

```python
async def trigger_nova_task_agent(
    user_number: str,
    whatsapp_service: WhatsAppService,
) -> dict:
    """Documentação da task."""
    try:
        logger.info('🎯 Iniciando tarefa: nova task')
        
        # Carrega prompt do arquivo
        prompt = _load_prompt('nova_task.md')
        
        # Processa com o agente
        result = await process_message_with_agent(
            user_number=user_number,
            message_text=prompt,
            whatsapp_service=whatsapp_service,
        )
        
        if result['status'] == 'ok':
            logger.success('✅ Nova task executada')
        else:
            logger.error(f'❌ Falha: {result["detail"]}')
        
        return result
    
    except Exception as e:
        logger.error(f'❌ Erro: {e}')
        return {'status': 'error', 'detail': str(e)}
```

### 4. Agendar a task

Em `app/scheduler.py`:

```python
# Importar a nova task
from .agents.tasks import trigger_nova_task_agent

# Adicionar job no setup_scheduler()
scheduler.add_job(
    func=_execute_nova_task,
    trigger=CronTrigger(hour=10, minute=0),
    id='nova_task_job',
    name='Nova Task',
    replace_existing=True,
    max_instances=1,
    coalesce=True,
    misfire_grace_time=300,
)

# Criar função auxiliar
async def _execute_nova_task() -> None:
    """Executa a nova task."""
    try:
        agora = datetime.now(ZoneInfo(BRAZIL_TZ))
        logger.info(f'🎯 [{agora}] Executando nova task')
        
        whatsapp_service = AppServices.get_whatsapp_service()
        result = await trigger_nova_task_agent(
            user_number=SCHEDULED_TASKS_USER_NUMBER,
            whatsapp_service=whatsapp_service,
        )
        
        if result['status'] == 'ok':
            logger.success('✅ Nova task executada')
        else:
            logger.error(f'❌ Falha: {result["detail"]}')
    
    except Exception as e:
        logger.error(f'❌ Erro: {e}')
```

## 🧪 Testando Prompts

### Teste Manual via WhatsApp

Envie a mensagem diretamente para o bot:

```
[Cole o conteúdo do prompt aqui]
```

O agente processará e você verá o resultado em tempo real.

### Teste Programático

```python
# tests/test_prompts.py
import pytest
from app.agents.tasks import _load_prompt

def test_load_instagram_prompt():
    prompt = _load_prompt('instagram_post.md')
    assert 'Instagram' in prompt
    assert 'legenda' in prompt.lower()
    assert len(prompt) > 100

def test_all_prompts_exist():
    prompts = [
        'instagram_post.md',
        'linkedin_post.md',
        'whatsapp_status.md',
        'sigaa_summary.md'
    ]
    
    for filename in prompts:
        prompt = _load_prompt(filename)
        assert prompt, f"Prompt {filename} está vazio"
```

## 📊 Métricas e Monitoramento

### Logs

Cada execução de prompt gera logs:

```
📸 [19/10/2025 15:00:00] Iniciando tarefa agendada: postagem no Instagram
🤖 Mensagem recebida para o agente: "[conteúdo do prompt]"
🔧 Usando ferramentas: list_drive_images, upload_photo...
✅ Postagem no Instagram realizada com sucesso
```

### Análise de Efetividade

Métricas a considerar:
- Taxa de sucesso das postagens
- Tempo médio de execução
- Qualidade do conteúdo gerado
- Engajamento nas plataformas

## 🔒 Segurança

### Validação de Entrada

Os prompts são arquivos estáticos, mas considere:

```python
def _load_prompt(filename: str) -> str:
    # Previne path traversal
    if '..' in filename or '/' in filename:
        raise ValueError("Nome de arquivo inválido")
    
    prompt_path = PROMPTS_DIR / filename
    
    # Verifica se está dentro do diretório permitido
    if not prompt_path.resolve().is_relative_to(PROMPTS_DIR.resolve()):
        raise ValueError("Caminho de arquivo não permitido")
    
    with open(prompt_path, 'r', encoding='utf-8') as f:
        return f.read().strip()
```

### Controle de Versão

- Sempre versione mudanças nos prompts via Git
- Documente alterações significativas
- Teste antes de fazer commit
- Mantenha backups de prompts funcionais

## 🔄 Versionamento de Prompts

### Estratégia Recomendada

Para manter histórico de mudanças importantes:

```
prompts/
├── v1/
│   ├── instagram_post.md
│   └── linkedin_post.md
├── v2/
│   ├── instagram_post.md  # Versão atualizada
│   └── linkedin_post.md
└── current/  # Symlink para versão ativa
    ├── instagram_post.md -> ../v2/instagram_post.md
    └── linkedin_post.md -> ../v2/linkedin_post.md
```

Ou usar o próprio Git para controle de versão.

## 💡 Dicas Avançadas

### Prompts Dinâmicos

Considere adicionar placeholders que são substituídos em tempo de execução:

```markdown
# Prompt: Instagram Post

Crie uma postagem para Instagram considerando:
- Horário: {CURRENT_TIME}
- Dia da semana: {DAY_OF_WEEK}
- Período: {PERIOD} (manhã/tarde/noite)

Ajuste o tom e tema conforme o contexto temporal.
```

```python
from datetime import datetime

def _load_prompt_with_context(filename: str) -> str:
    prompt = _load_prompt(filename)
    
    now = datetime.now()
    context = {
        'CURRENT_TIME': now.strftime('%H:%M'),
        'DAY_OF_WEEK': now.strftime('%A'),
        'PERIOD': 'manhã' if now.hour < 12 else 'tarde' if now.hour < 18 else 'noite'
    }
    
    for key, value in context.items():
        prompt = prompt.replace(f'{{{key}}}', value)
    
    return prompt
```

### Prompts Condicionais

```python
def _load_conditional_prompt(base_filename: str) -> str:
    """Carrega prompt com variações por contexto."""
    now = datetime.now()
    
    # Tenta carregar versão específica do dia
    day_variant = f"{base_filename.replace('.md', '')}_{now.strftime('%A').lower()}.md"
    
    try:
        return _load_prompt(day_variant)
    except FileNotFoundError:
        # Fallback para prompt padrão
        return _load_prompt(base_filename)
```

---

**Última atualização:** 19 de outubro de 2025  
**Mantido por:** Klique API Team
