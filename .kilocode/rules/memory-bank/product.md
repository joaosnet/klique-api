# Produto: Klique WhatsApp Bot

## Visão Geral

O Klique WhatsApp Bot transforma a Klique API em um serviço interativo de geração de imagens diretamente no WhatsApp. Os usuários podem enviar prompts de texto em uma conversa e receber imagens geradas por IA, que são também publicadas automaticamente como status do WhatsApp.

## Problema Resolvido

O serviço elimina a necessidade de um aplicativo separado, integrando a geração de imagens ao fluxo de comunicação diário dos usuários no WhatsApp. Ele oferece uma forma lúdica e instantânea de criar e compartilhar conteúdo visual.

## Como Funciona

1.  **Recebimento de Mensagens (Webhook):** A API (fastapi-app) recebe notificações (webhooks) do gateway `go-whatsapp` sempre que um usuário envia uma mensagem.
2.  **Processamento de Prompt:** A API extrai o texto da mensagem para ser usado como prompt para a geração da imagem.
3.  **Integração com IA:** A API envia o prompt para o serviço do Gemini, que gera a imagem correspondente.
4.  **Envio de Resposta:** A API utiliza a interface REST do `go-whatsapp` para:
    *   Enviar a imagem gerada diretamente para a conversa com o usuário.
    *   Publicar a mesma imagem como um novo status na conta do WhatsApp conectada.

## Objetivos de Experiência do Usuário

*   **Interatividade:** A experiência deve ser conversacional e instantânea, como um bate-papo normal.
*   **Simplicidade:** O usuário só precisa enviar um texto; o bot cuida de todo o resto.
*   **Engajamento:** A publicação automática de status gera visibilidade e incentiva o uso contínuo.