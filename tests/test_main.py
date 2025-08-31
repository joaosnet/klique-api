from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from main import app

def test_generate_success():
    with TestClient(app) as client:
        response = client.post("/generate", json={"prompt": "Olá, mundo!"})

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["text"], str)
    assert len(data["text"]) > 0
    assert isinstance(data["candidates"], list)
    assert isinstance(data["images"], list)
    assert isinstance(data["metadata"], list)

def test_batch_success():
    with TestClient(app) as client:
        response = client.post("/batch", json={"prompts": ["prompt 1", "prompt 2"]})

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 2
    for result in data["results"]:
        assert "index" in result
        assert "text" in result
        assert isinstance(result["text"], str)
        assert len(result["text"]) > 0