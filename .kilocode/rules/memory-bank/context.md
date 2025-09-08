# Contexto (Atualizado em Setembro 2025)

## Estado Atual do Sistema

O Klique WhatsApp Bot está em produção estável com arquitetura madura e funcionalidades completas implementadas. O sistema opera através de comandos explícitos, tendo removido o processamento automático de mensagens livres para maior controle e previsibilidade. A implementação atual utiliza uma abordagem híbrida com dois serviços de geração de imagens disponíveis.

## Funcionalidades Implementadas

### Sistema de Comandos Estruturado
- **Comandos implementados**: `imagem`, `legenda`, `refazer`, `editar`, `ajuda`
- **Parser robusto**: Sistema em [`command.py`](app/command.py:1) com `CommandOperation` enum e `CommandContext`
- **Processamento assíncrono**: Comandos são executados em background tasks para resposta rápida
- **Feedback imediato**: Mensagens de confirmação antes do processamento pesado

### Cache e Sessão Avançados
- **Cache unificado MongoDB**: Sistema implementado em [`cache.py`](app/cache.py:1) usando apenas MongoDB
- **Sessões por usuário**: `UserSessionCache` mantém estado individual (prompt, imagens, status_id)
- **Cache de status global**: `StatusImageCache` para geração automática em visualizações
- **Sistema anti-duplicação**: `MessageCache` previne reprocessamento de mensagens

### Geração Automática de Status
- **Trigger por visualização**: Gera nova imagem personalizada quando alguém visualiza status
- **Personalização dinâmica**: Inclui nome do visualizador na imagem gerada
- **Substituição inteligente**: Remove status anterior automaticamente antes de postar novo

### Integração Dupla com Gemini
- **Serviço Oficial**: [`GeminiService`](app/services/gemini.py:1) usando `google-genai` (serviço principal)
- **Serviço Web API**: [`GeminiWebApiService`](app/services/gemini_webapi_service.py:1) usando `gemini-webapi` (alternativo)
- **Enhancement de prompts**: `gemini-2.5-flash-lite` aprimora prompts automaticamente
- **Suporte image-to-image**: Aceita imagens como entrada para edição/variação

## Arquitetura Atual

### Processamento Webhook Otimizado
- Resposta imediata com feedback de processamento em [`whatsapp.py`](app/routers/whatsapp.py:1)
- Background tasks para operações pesadas
- Sistema robusto de tratamento de erros e fallbacks

### Implementação Híbrida de Serviços
- **Serviço Principal**: Google GenAI oficial para confiabilidade
- **Serviço Alternativo**: Gemini Web API para funcionalidades adicionais e backup
- **Testes Integrados**: Ambos os serviços têm testes automatizados

### Dependências Estáveis
- `google-genai`: Biblioteca oficial do Google (serviço principal)
- `gemini-webapi`: Biblioteca web alternativa mantida para compatibilidade
- Cache unificado MongoDB (sem dependências de cache em memória)
- Sistema de logs melhorado com `loguru` e Rich

## Próximos Desenvolvimentos

O sistema está maduro e estável, pronto para:
- Expansão de comandos (V2) mantendo compatibilidade
- Melhorias na UX dos comandos existentes
- Otimizações de performance conforme demanda
- Possível consolidação dos serviços de geração baseada no uso