# Produto: Klique WhatsApp Bot

## Visão Geral

O Klique WhatsApp Bot transforma a Klique API em um serviço interativo de geração de imagens diretamente no WhatsApp. Os usuários podem enviar prompts de texto em uma conversa e receber imagens geradas por IA, que são também publicadas automaticamente como status do WhatsApp.

## Problema Resolvido

O serviço elimina a necessidade de um aplicativo separado, integrando a geração de imagens ao fluxo de comunicação diário dos usuários no WhatsApp. Ele oferece uma forma lúdica e instantânea de criar e compartilhar conteúdo visual.

## Como Funciona

1.  **Recebimento de Mensagens (Webhook):** A API (fastapi-app) recebe notificações (webhooks) do gateway `go-whatsapp` sempre que um usuário envia uma mensagem.
2.  **Sistema de Comandos:** O sistema reconhece comandos específicos (`imagem`, `legenda`, `refazer`, `editar`, `ajuda`) em vez de processar mensagens livres automaticamente.
3.  **Processamento de Prompt:** Para comandos de geração, a API extrai o prompt e aprimora-o automaticamente usando o Gemini antes da geração.
4.  **Integração com IA:** A API utiliza o modelo `gemini-2.5-flash-image-preview` para gerar imagens, com suporte completo a image-to-image.
5.  **Envio de Resposta:** A API utiliza a interface REST do `go-whatsapp` para:
    *   Enviar a imagem gerada diretamente para a conversa com o usuário.
    *   Publicar a mesma imagem como um novo status na conta do WhatsApp conectada.
6.  **Geração Automática:** Quando alguém visualiza um status, o sistema gera automaticamente uma nova imagem personalizada com o nome do visualizador.

## Objetivos de Experiência do Usuário

*   **Controle Explícito:** O usuário utiliza comandos específicos para cada ação, garantindo previsibilidade e controle total.
*   **Simplicidade:** Sistema de comandos intuitivo (`imagem <prompt>`, `refazer`, `editar <instruções>`, etc.).
*   **Persistência de Sessão:** O sistema lembra do último prompt e imagens geradas, permitindo edições e variações.
*   **Engajamento:** A publicação automática de status e geração personalizada para visualizadores aumenta a interação.
*   **Feedback Imediato:** Resposta instantânea aos comandos com processamento em background para operações pesadas.
*   **Feedback Claro:** Mensagens de ajuda e orientação quando comandos são usados incorretamente ou falham.