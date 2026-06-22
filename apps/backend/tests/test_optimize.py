from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "environment": "testing"}


@pytest.mark.asyncio
async def test_optimize_validation_error(client):
    # Prompt requires minimum 3 characters
    response = await client.post("/api/v1/optimize", json={"prompt": "ab"})
    assert response.status_code == 422
    assert "prompt" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_optimize_missing_fields(client):
    # Prompt is missing
    response = await client.post("/api/v1/optimize", json={"tone": "concise"})
    assert response.status_code == 422
    assert "prompt" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_optimize_success(client, mock_groq_response):
    with patch("app.services.groq.AsyncGroq") as mock_async_groq:
        mock_instance = mock_async_groq.return_value

        # Structure mock return
        mock_choice = AsyncMock()
        mock_choice.message = AsyncMock()
        mock_choice.message.content = mock_groq_response["choices"][0]["message"][
            "content"
        ]

        mock_completions = AsyncMock()
        mock_completions.choices = [mock_choice]

        mock_instance.chat.completions.create = AsyncMock(return_value=mock_completions)

        payload = {
            "prompt": "How to write a FastAPI server?",
            "tone": "professional",
            "detail_level": "detailed",
            "target_audience": "developers",
        }

        response = await client.post("/api/v1/optimize", json=payload)

        assert response.status_code == 200
        res_data = response.json()
        assert res_data["raw_prompt"] == "How to write a FastAPI server?"
        assert "Act as an expert FastAPI developer" in res_data["optimized_prompt"]
        assert "Added developer persona" in res_data["explanation"]
        assert "metrics" in res_data
        assert res_data["metrics"]["tokens_before"] > 0
        assert res_data["metrics"]["tokens_after"] > 0
        assert res_data["metrics"]["processing_time_ms"] >= 0.0
