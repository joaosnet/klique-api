# Configuração da Gemini Web API no Docker

Este documento explica como configurar corretamente a `gemini-webapi` para funcionar em ambiente Docker.

## Problema

A biblioteca `gemini-webapi` utiliza cookies do navegador para autenticação. Em ambientes Docker, esses cookies não estão disponíveis, causando erros como:

```
Failed to initialize client. SECURE_1PSIDTS could get expired frequently, please make sure cookie values are up to date.
```

## Solução

### 1. Obter os Cookies

1. Acesse https://gemini.google.com e faça login com sua conta Google
2. Abra as ferramentas de desenvolvedor (F12)
3. Vá para a aba `Network` e recarregue a página
4. Clique em qualquer requisição e procure pelos cookies:
   - `__Secure-1PSID`
   - `__Secure-1PSIDTS`

### 2. Configurar as Variáveis de Ambiente

Crie ou edite o arquivo `.env` na raiz do projeto com:

```env
# Cookies para a Gemini Web API
SECURE_1PSID="valor_do_cookie_secure_1psid"
SECURE_1PSIDTS="valor_do_cookie_secure_1psidts"
```

### 3. Volume para Persistência

O `docker-compose.yml` já está configurado com um volume para persistir os cookies:

```yaml
volumes:
  - gemini_cookies:/usr/local/lib/python3.12/site-packages/gemini_webapi/utils/temp
```

Isso evita que os cookies sejam perdidos entre reinicializações do container.

### 4. Executar o Sistema

```bash
docker-compose up -d
```

## Observações

- Os cookies podem expirar periodicamente e precisarão ser atualizados
- A biblioteca tem função de auto-refresh habilitada para tentar manter os cookies válidos
- Caso continue com problemas, verifique se os cookies não expiraram e obtenha novos valores

## Referência

Documentação oficial da gemini-webapi: https://github.com/HanaokaYuzu/Gemini-API