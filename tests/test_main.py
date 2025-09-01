import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_batch_route_returns_results():
    from main import app

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/batch",
            json={
                "prompts": ["Olá Gemini!", "Teste batch"],
                "model": "unspecified",
                "gem": None
            }
        )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)
    assert len(data["results"]) == 2
    for item in data["results"]:
        assert "index" in item
        assert "text" in item or "error" in item