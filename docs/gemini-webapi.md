# gemini-webapi atualizada

Este projeto está integrado com a biblioteca gemini-webapi para geração e edição de imagens via Gemini Web.

Em 06/03/2026, a documentação pública mais recente consultada indicava:

- PyPI em 1.20.0
- README oficial do repositório HanaokaYuzu/Gemini-API
- suporte nativo para geração e edição de imagens via generate_content

## Instalação

```bash
pip install -U gemini_webapi
```

Opcionalmente, para importar cookies do browser:

```bash
pip install -U browser-cookie3
```

## Inicialização recomendada

```python
from gemini_webapi import GeminiClient

client = GeminiClient(SECURE_1PSID, SECURE_1PSIDTS, proxy=None)
await client.init(
    timeout=30,
    auto_close=True,
    close_delay=10,
    auto_refresh=True,
)
```

Notas práticas:

- auto_refresh mantém o cookie atualizado em serviços long-lived
- auto_close com close_delay ajuda a liberar recursos em períodos ociosos
- em containers, a documentação recomenda persistir cookies com GEMINI_COOKIE_PATH

## Geração de texto

```python
response = await client.generate_content('Explain the Pareto principle.')
print(response.text)
```

## Geração de imagem

Para obter imagens geradas por IA, o prompt deve pedir explicitamente para gerar ou criar uma imagem. Pedidos vagos podem retornar imagens da web em vez de imagens geradas.

```python
response = await client.generate_content(
    'Generate an original image of a futuristic chess board. '
    'Do not send web images.'
)

image = response.images[0]
await image.save(
    path='generated_media/cards',
    filename='example.png',
    full_size=True,
)
```

Notas práticas:

- response.images pode conter WebImage ou GeneratedImage
- para imagens geradas, prefira o método nativo image.save(..., full_size=True)
- evitar download manual por image.url quando o objeto já expõe save com cookies corretos

## Edição de imagem

A API atual aceita arquivos via parâmetro files.

```python
response = await client.generate_content(
    'Edit the provided image and make it look more cinematic. '
    'Do not send web images.',
    files=['generated_media/cards/original.png'],
)

edited_image = response.images[0]
await edited_image.save(
    path='generated_media/cards',
    filename='edited.png',
    full_size=True,
)
```

Também é possível enviar bytes:

```python
file_bytes = await upload_file.read()
response = await client.generate_content(
    'Analyze the uploaded card design and recreate it as SVG.',
    files=[file_bytes],
)
```

## Padrão adotado neste backend

As correções feitas no projeto seguem estas regras:

- geração e edição usam generate_content com files quando houver imagem base
- salvamento usa image.save em vez de download manual por URL
- prompts de imagem deixam explícito que a resposta deve ser uma imagem gerada, não uma busca na web
- inicialização do cliente usa timeout, auto_close, close_delay e auto_refresh
- prompts de domínio, card e avatar foram centralizados no serviço para manter consistência visual
- melhoria de card, domínio e avatar usa o mesmo fluxo de edição com imagem base quando disponível

## Referência rápida

- texto: client.generate_content(prompt)
- imagem nova: client.generate_content(prompt_explicito_de_geracao)
- editar imagem: client.generate_content(prompt, files=[caminho_ou_bytes])
- salvar imagem: await response.images[0].save(...)