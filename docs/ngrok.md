# 🔧 Testando a API com ngrok

Este projeto agora inclui um script de apoio para criar um túnel ngrok local em `app/scripts/ngrok.py`.

Passos rápidos:

1. (Opcional, recomendado) Configure o token do ngrok em uma variável de ambiente ou use um arquivo `.ngrok.env` no root do projeto:

   ```bash
   # alternativa 1: variável de ambiente (temporária neste shell)
   export NGROK_AUTH_TOKEN=seu_token_aqui
   # no Windows PowerShell (temporário nesta sessão):
   $env:NGROK_AUTH_TOKEN = "seu_token_aqui"

   # alternativa 2: crie `.ngrok.env` no diretório raiz do projeto com o conteúdo:
   # NGROK_AUTH_TOKEN=seu_token_aqui
   ```

   Para facilitar, há um arquivo de exemplo em `.ngrok.env.example` que você pode copiar para `.ngrok.env` e preencher com seu token.

2. Inicie a aplicação localmente (por exemplo em outra janela/terminal):

   ```bash
   task run
   # ou diretamente: fastapi dev app/main.py --host 0.0.0.0
   ```

3. Abra o túnel ngrok:

   ```bash
   task ngrok
   # por padrão o script usa a porta 8000; para outra porta:
   task ngrok -- --port 8080
   ```

4. O script imprimirá a URL pública do ngrok (ex: `https://abcd-12-34-56.ngrok.io`). Use essa URL para testar webhooks e integrações externas.

Observações:

- `pyngrok` foi adicionado como dependência de desenvolvimento via `uv add --dev pyngrok`.
- Se preferir, você pode usar o cliente ngrok oficial em vez do `pyngrok` (ex.: `ngrok http 8000`).
- Mantenha o processo rodando para manter o túnel ativo.
