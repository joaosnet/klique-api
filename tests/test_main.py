from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock

# Adiciona o diretório src ao path para que possamos importar o 'main'
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from main import app

# O patch precisa ser aplicado onde o objeto é criado, ou seja, em 'src.services.gemini'
@patch('src.services.gemini.GeminiClient')
def test_generate_success(mock_gemini_client_class):
    # Configura o mock da instância que será criada
    mock_instance = MagicMock()
    mock_instance.init = AsyncMock()
    mock_instance.close = AsyncMock()
    
    # Configura o retorno do método que queremos testar
    mock_response = MagicMock()
    mock_response.text = "Texto gerado com sucesso"
    mock_response.candidates = [MagicMock(text="candidato 1")]
    mock_response.images = [MagicMock(url="http://imagem.url")]
    mock_response.metadata = {"chat_id": "123"}
    mock_instance.generate_content = AsyncMock(return_value=mock_response)

    # A classe mockada retorna nossa instância mockada
    mock_gemini_client_class.return_value = mock_instance

    with TestClient(app) as client:
        response = client.post("/generate", json={"prompt": "Olá, mundo!"})

    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Texto gerado com sucesso"
    assert data["candidates"] == ["candidato 1"]
    assert data["images"] == ["http://imagem.url"]
    assert data["metadata"] == {"chat_id": "123"}
    mock_instance.generate_content.assert_called_once()

@patch('src.services.gemini.GeminiClient')
def test_batch_success(mock_gemini_client_class):
    # Configura o mock da instância
    mock_instance = MagicMock()
    mock_instance.init = AsyncMock()
    mock_instance.close = AsyncMock()

    # Configura o side_effect para o método generate_content
    async def side_effect(*args, **kwargs):
        prompt = kwargs.get("prompt")
        if prompt == "prompt 1":
            return MagicMock(text="resultado 1")
        elif prompt == "prompt 2":
            return MagicMock(text="resultado 2")
        return MagicMock(text="resultado padrao")

    mock_instance.generate_content = AsyncMock(side_effect=side_effect)
    mock_gemini_client_class.return_value = mock_instance

    with TestClient(app) as client:
        response = client.post("/batch", json={"prompts": ["prompt 1", "prompt 2"]})

    assert response.status_code == 200
    data = response.json()
    assert data["results"] == [
        {"index": 0, "text": "resultado 1"},
        {"index": 1, "text": "resultado 2"},
    ]
    assert mock_instance.generate_content.call_count == 2