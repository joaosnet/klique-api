# Produto: Klique API

## Visão Geral

A Klique API é o serviço de backend para o aplicativo Klique, uma ferramenta de edição de imagens que permite aos usuários modificar suas fotos usando prompts de texto simples. A API orquestra a comunicação entre o aplicativo cliente (frontend) e os modelos de inteligência artificial da Google (Gemini) para gerar as imagens editadas.

## Problema Resolvido

A API abstrai a complexidade de interagir diretamente com modelos de IA, fornecendo endpoints simples e seguros para o aplicativo cliente. Ela gerencia a autenticação, o controle de uso, o processamento de prompts e a manipulação de imagens, permitindo que o frontend se concentre na experiência do usuário.

## Como Funciona

1.  **Recebimento de Requisições:** A API recebe requisições do aplicativo cliente contendo um prompt de texto, uma imagem opcional e um token de autenticação.
2.  **Processamento:** A API valida a requisição, processa o prompt e a imagem.
3.  **Integração com IA:** Envia os dados para a API do Gemini para gerar a imagem ou conteúdo solicitado.
4.  **Gerenciamento de Sessão:** Mantém o contexto das conversas (chats) para permitir edições interativas e contínuas.
5.  **Retorno:** Retorna a imagem gerada (em formato base64) ou o texto para o aplicativo cliente.

## Objetivos de Experiência do Usuário (através da API)

*   **Rapidez:** A API deve responder rapidamente para que o usuário veja o resultado da edição quase em tempo real.
*   **Confiabilidade:** A API deve ser estável e lidar com erros de forma previsível (ex: limites de uso, erros do modelo de IA).
*   **Segurança:** A comunicação entre o cliente e a API deve ser segura.