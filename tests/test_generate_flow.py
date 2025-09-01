import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient
import io
import httpx
import os
import base64
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Adiciona o diretório raiz do projeto ao sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import app

# URL base da API para testes de integração
BASE_URL = "http://127.0.0.1:8000"
TEST_IMAGE_PATH = Path(__file__).parent / "assets" / "test_image.png"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_generate_image_no_token(client):
    data = {"prompt": "test"}
    response = client.post("/generate/image", data=data)
    assert response.status_code == 401
    assert "Authorization header missing" in response.json()["detail"]


@pytest.mark.integration
def test_full_image_editing_and_storage_flow(client):
    """
    Testa o fluxo completo de edição e armazenamento de imagens, incluindo:
    1. Edição inicial com uma imagem.
    2. Edição contínua na mesma sessão.
    3. Edição com múltiplas imagens para combinação de estilos.
    """
    auth_token = os.getenv("AUTH_TOKEN")
    assert auth_token, "O AUTH_TOKEN não foi encontrado nas variáveis de ambiente."

    headers = {"Authorization": f"Bearer {auth_token}"}

    # -- Cenário 1: Edição de Imagem Única e Armazenamento --
    first_prompt = "adicione um chapéu de pirata"
    
    assert TEST_IMAGE_PATH.exists(), f"Imagem de teste não encontrada: {TEST_IMAGE_PATH}"

    with open(TEST_IMAGE_PATH, "rb") as f:
        files = {"image_file": ("test_image.png", f, "image/png")}
        data = {"prompt": first_prompt}
        
        response1 = client.post(
            "/generate/image", headers=headers, data=data, files=files
        )

    assert response1.status_code == 200, f"Erro na primeira requisição: {response1.text}"
    response1_data = response1.json()
    assert "generated_image" in response1_data
    assert "session_id" in response1_data
    assert response1_data["generated_image"] is not None

    session_id = response1_data["session_id"]
    
    # -- Cenário 2: Edição Contínua na Mesma Sessão --
    second_prompt = "agora adicione um tapa-olho"
    data = {"prompt": second_prompt, "session_id": session_id}
    
    response2 = client.post("/generate/image", headers=headers, data=data)

    assert response2.status_code == 200, f"Erro na segunda requisição: {response2.text}"
    response2_data = response2.json()
    assert "generated_image" in response2_data
    assert response2_data["session_id"] == session_id
    assert response2_data["generated_image"] is not None
    assert response1_data["generated_image"] != response2_data["generated_image"]

    # -- Cenário 3: Edição com Múltiplas Imagens --
    multi_image_prompt = "combine o estilo da segunda imagem na primeira"
    
    with open(TEST_IMAGE_PATH, "rb") as f1, open(TEST_IMAGE_PATH, "rb") as f2:
        files = [
            ("image_files", ("test_image1.png", f1, "image/png")),
            ("image_files", ("test_image2.png", f2, "image/png")),
        ]
        data = {"prompt": multi_image_prompt}
        
        response3 = client.post(
            "/generate/image", headers=headers, data=data, files=files
        )

    assert response3.status_code == 200, f"Erro na requisição com múltiplas imagens: {response3.text}"
    response3_data = response3.json()
    assert "generated_image" in response3_data
    assert "session_id" in response3_data
    assert response3_data["generated_image"] is not None
