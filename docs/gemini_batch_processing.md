# Processamento em Lote de Geração de Imagens com `gemini-webapi`

A biblioteca `gemini-webapi` não oferece uma função de processamento em lote nativa para a geração de conteúdo ou imagens. No entanto, é possível simular o processamento em lote utilizando as capacidades assíncronas do Python e executando múltiplas chamadas à função `generate_content` de forma concorrente.

Esta abordagem é eficiente para lidar com um volume maior de requisições de forma não bloqueante, aproveitando o `asyncio` para gerenciar as operações.

## Abordagem

Para simular o processamento em lote, utilizaremos:

1.  **`asyncio.gather`**: Para executar múltiplas corrotinas (`async def` functions) concorrentemente.
2.  **`GeminiClient.generate_content`**: A função principal para enviar prompts e gerar conteúdo/imagens.

## Exemplo de Código

O exemplo abaixo demonstra como enviar múltiplos prompts para geração de imagens de forma assíncrona e processar os resultados.

```python
import asyncio
from gemini_webapi import GeminiClient
from pathlib import Path
import base64

# Substitua com seus valores de cookie reais
# Secure_1PSID = "SEU_COOKIE_SECURE_1PSID"
# Secure_1PSIDTS = "SEU_COOKIE_SECURE_1PSIDTS"

async def process_single_request(client: GeminiClient, prompt: str, image_path: Path = None):
    """
    Processa uma única requisição de geração de imagem.
    """
    try:
        if image_path:
            print(f"Gerando para prompt: '{prompt}' com imagem: {image_path.name}")
            response = await client.generate_content(prompt, files=[image_path])
        else:
            print(f"Gerando para prompt: '{prompt}'")
            response = await client.generate_content(prompt)

        generated_image_data = None
        if response.images:
            # Assumindo que queremos a primeira imagem gerada
            # Para salvar, você pode usar await response.images[0].save(...)
            # Ou obter os dados base64 se necessário para a API
            # Exemplo de como obter dados da imagem (pode variar dependendo da implementação interna da Image object)
            # Isso é um placeholder, a forma exata de obter o base64 da imagem gerada pode precisar de adaptação.
            # Se 'response.images[0]' já retornar um objeto de imagem que pode ser convertido para bytes ou base64
            # você precisaria de um método para isso (e.g., .to_base64() ou .get_bytes())
            # Por simplicidade, aqui assumimos que `response.images[0]` é um objeto com um método `to_base64` ou similar
            # ou que você vai salvá-la e depois ler.
            # Para este exemplo, vamos apenas indicar que uma imagem foi gerada.
            generated_image_data = f"Imagem gerada: {response.images[0].url if hasattr(response.images[0], 'url') else 'disponível'}"
        
        return {
            "prompt": prompt,
            "response_text": response.text,
            "generated_image_info": generated_image_data,
            "status": "sucesso"
        }
    except Exception as e:
        print(f"Erro ao processar prompt '{prompt}': {e}")
        return {
            "prompt": prompt,
            "response_text": None,
            "generated_image_info": None,
            "status": f"erro: {e}"
        }

async def batch_generate_images(client: GeminiClient, requests: list):
    """
    Simula o processamento em lote de requisições de geração de imagem.
    
    Args:
        client: Uma instância de GeminiClient.
        requests: Uma lista de dicionários, onde cada dicionário contém:
                  - "prompt": O texto do prompt.
                  - "image_path": (Opcional) Caminho para a imagem a ser usada no prompt.
    """
    tasks = []
    for req in requests:
        prompt = req["prompt"]
        image_path = Path(req["image_path"]) if "image_path" in req else None
        tasks.append(process_single_request(client, prompt, image_path))
    
    results = await asyncio.gather(*tasks)
    return results

async def main():
    # Inicializa o cliente Gemini
    # Se você instalou browser-cookie3, pode usar client = GeminiClient()
    # Caso contrário, descomente e preencha com seus cookies:
    # client = GeminiClient(Secure_1PSID, Secure_1PSIDTS)
    client = GeminiClient() # Usando o construtor padrão com browser-cookie3

    await client.init(timeout=30, auto_close=False, close_delay=300, auto_refresh=True)

    # Lista de requisições para o processamento em lote
    batch_requests = [
        {"prompt": "Gere uma imagem de um gato astronauta."},
        {"prompt": "Crie uma paisagem de floresta encantada com um rio.", "image_path": "tests/assets/test_image.png"}, # Exemplo com imagem
        {"prompt": "Desenhe um robô amigável segurando uma flor."}
    ]

    print("Iniciando processamento em lote...")
    results = await batch_generate_images(client, batch_requests)
    print("\nResultados do processamento em lote:")
    for result in results:
        print(f"- Prompt: {result['prompt']}")
        print(f"  Status: {result['status']}")
        if result['response_text']:
            print(f"  Texto Resposta: {result['response_text'][:50]}...") # Limita para não poluir
        if result['generated_image_info']:
            print(f"  Imagem Gerada: {result['generated_image_info']}")
        print("-" * 20)

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Como Integrar na sua API FastAPI (src/routers/batch.py)

Para integrar essa funcionalidade na sua API FastAPI, você pode criar um novo endpoint em `src/routers/batch.py` que aceita uma lista de prompts e/ou imagens.

1.  **Definir um Pydantic Model para as Requisições em Lote**:
    Crie um modelo para a entrada de cada requisição individual e um para a lista de requisições.

    ```python
    # src/routers/batch.py (exemplo)
    from pydantic import BaseModel, Field
    from typing import List, Optional
    from fastapi import APIRouter, Depends, UploadFile, File, Form
    from fastapi import Request, HTTPException, status
    import asyncio
    from src.services.gemini import GeminiService
    from src.config import settings

    class BatchImageGenerationRequest(BaseModel):
        prompt: str = Field(..., description="O prompt de texto para a geração da imagem.")
        # Para imagens, você precisará de um mecanismo para lidar com o upload de múltiplos arquivos
        # ou passar URLs/base64 se as imagens já estiverem em algum lugar.
        # Este exemplo assume que a imagem será tratada separadamente ou codificada em base64 se enviada no JSON.
        # Para múltiplos uploads de arquivos em FastAPI, a abordagem é diferente para cada arquivo.
        # Para simplificar aqui, consideraremos a imagem como opcional e não parte direta do JSON do BaseModel,
        # ou que ela seria um base64 string.
        image_base64: Optional[str] = Field(None, description="Imagem opcional codificada em base64.")

    class BatchRequest(BaseModel):
        requests: List[BatchImageGenerationRequest]

    router = APIRouter()

    @router.post("/batch/generate/image")
    async def batch_generate_image_endpoint(
        batch_data: BatchRequest,
        request: Request
    ):
        gemini_service: GeminiService = request.app.state.gemini_service
        
        # Lista de tarefas assíncronas
        tasks = []
        for req in batch_data.requests:
            image_data = None
            if req.image_base64:
                # Decodificar base64 para bytes, se necessário.
                # Para o GeminiClient, talvez precise salvar temporariamente ou passar bytes diretamente
                try:
                    image_data = base64.b64decode(req.image_base64)
                    # Você precisaria de uma forma de passar 'image_data' como um "arquivo" para generate_content
                    # GeminiClient.generate_content espera 'files' como lista de paths ou objetos de arquivo.
                    # Isso pode exigir uma refatoração em GeminiService.send_message para aceitar bytes/UploadedFile.
                    # Por enquanto, vamos manter a lógica de processamento_single_request como está,
                    # e a integração real dependerá de como `GeminiService` pode aceitar os dados da imagem.
                    # Para um MVP, pode ser mais simples ter o cliente enviando o caminho para um arquivo temporário
                    # que a API salva primeiro, ou um upload de arquivo separado para cada item do lote.
                    print("Decodificando imagem base64 - integração completa requer adaptação do GeminiService.")
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Erro ao decodificar imagem base64: {e}")

            # Adapte a chamada para o GeminiService.send_message
            # Dependendo de como seu GeminiService está configurado para receber imagens
            # Atualmente, o GeminiService.send_message espera um Path ou UploadFile
            # Você precisaria de um helper para converter base64 para um objeto de arquivo temporário se necessário.
            tasks.append(
                asyncio.create_task(
                    gemini_service.send_message(
                        chat=None, # Para geração de imagem, não necessariamente uma sessão de chat contínua
                        prompt=req.prompt,
                        image_file=image_data # Isso precisaria ser um UploadFile ou Path
                    )
                )
            )
        
        results = await asyncio.gather(*tasks, return_exceptions=True) # Captura exceções para cada tarefa
        
        processed_results = []
        for i, res in enumerate(results):
            if isinstance(res, Exception):
                processed_results.append({
                    "prompt": batch_data.requests[i].prompt,
                    "status": "erro",
                    "detail": str(res)
                })
            else:
                # Assumindo que 'res' é a resposta do GeminiService.send_message
                # E que ela contém a imagem gerada e o texto
                generated_image_base64 = None
                if res.images: # Se o resultado do GeminiService tiver uma lista de imagens
                    # Você precisaria de uma forma de converter a imagem de volta para base64 para o cliente
                    # Exemplo: generated_image_base64 = base64.b64encode(res.images[0].bytes).decode('utf-8')
                    # Isso depende da estrutura do objeto Image retornado pelo gemini-webapi
                    pass # Implementar conversão para base64
                
                processed_results.append({
                    "prompt": batch_data.requests[i].prompt,
                    "response_text": res.text,
                    "generated_image_base64": generated_image_base64,
                    "status": "sucesso"
                })
        
        return {"batch_results": processed_results}
    ```

## Considerações Importantes

*   **Autenticação**: Certifique-se de que o `GeminiClient` esteja corretamente inicializado com os cookies de sessão ou outras credenciais necessárias.
*   **Limites de Taxa (Rate Limits)**: A execução de múltiplas requisições concorrentes pode atingir os limites de taxa da API do Gemini. Monitore e implemente mecanismos de `rate limiting` ou `backoff` se necessário.
*   **Gerenciamento de Erros**: O exemplo inclui um tratamento básico de erros para requisições individuais. Em um ambiente de produção, um tratamento mais robusto é essencial.
*   **Memória e Performance**: Lidar com múltiplas imagens pode consumir bastante memória. Otimize o carregamento e o processamento de imagens conforme necessário.
*   **FastAPI e Upload de Múltiplos Arquivos**: Se você precisa enviar múltiplas imagens como arquivos no endpoint da FastAPI, a abordagem com `UploadFile` é um pouco mais complexa para requisições em lote dentro de um único JSON. Você pode considerar enviar as imagens separadamente ou codificá-las em base64 no JSON, como sugerido no exemplo da FastAPI, mas exigirá adaptações no `GeminiService`. Para este exemplo, a `image_path` é um placeholder para um arquivo local.
*   **`GeminiService` Adaptação**: O `GeminiService` atual em `src/services/gemini.py` pode precisar de adaptações para aceitar dados de imagem em diferentes formatos (e.g., bytes, objetos `UploadFile` diretamente) para facilitar a integração com a rota de lote.
