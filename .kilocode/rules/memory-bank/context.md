# Contexto (Atualizado em Janeiro 2025)

## Estado Atual do Sistema

O Klique WhatsApp Bot está em produção com uma arquitetura madura e funcionalidades completas implementadas. O sistema opera através de comandos explícitos, tendo removido o processamento automático de mensagens livres para maior controle e previsibilidade.

## Funcionalidades Implementadas

### Sistema de Comandos Estruturado
- **Comandos implementados**: `imagem`, `legenda`, `refazer`, `editar`, `ajuda`
- **Parser robusto**: Sistema em `command.py` com `CommandOperation` enum e `CommandContext`
- **Processamento assíncrono**: Comandos são executados em background tasks para resposta rápida

### Cache e Sessão Avançados
- **Cache unificado MongoDB**: Substituiu completamente sistema híbrido anterior
- **Sessões por usuário**: `UserSessionCache` mantém estado individual (prompt, imagens, status_id)
- **Cache de status global**: `StatusImageCache` para geração automática em visualizações
- **Sistema anti-duplicação**: `MessageCache` previne reprocessamento

### Geração Automática de Status
- **Trigger por visualização**: Gera nova imagem quando alguém visualiza status
- **Personalização dinâmica**: Inclui nome do visualizador na imagem
- **Substituição inteligente**: Remove status anterior automaticamente

### Integração com Gemini Avançada
- **Modelo atual**: `gemini-2.5-flash-image-preview` para geração
- **Enhancement de prompts**: `gemini-2.5-flash-lite` aprimora prompts automaticamente
- **Suporte image-to-image**: Aceita imagens como entrada para edição/variação

## Arquitetura Atual

### Processamento Webhook Otimizado
- Resposta imediata com feedback de processamento
- Background tasks para operações pesadas
- Sistema robusto de tratamento de erros

### Dependências Atualizadas
- `google-genai`: Biblioteca oficial atual (substituiu `gemini-webapi`)
- Cache unificado MongoDB (removeu dependências de cache em memória)
- Sistema de logs melhorado com `loguru` e Rich

## Próximos Desenvolvimentos

O sistema está estável e pronto para:
- Expansão de comandos (V2)
- Melhorias na UX dos comandos existentes
- Otimizações de performance conforme necessário