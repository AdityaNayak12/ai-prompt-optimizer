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


@pytest.mark.asyncio
async def test_optimize_gets_shorter(client):
    with patch("app.services.groq.AsyncGroq") as mock_async_groq:
        mock_instance = mock_async_groq.return_value

        mock_choice = AsyncMock()
        mock_choice.message = AsyncMock()
        mock_choice.message.content = (
            '{\n'
            '  "optimized_prompt": "Optimize long text.",\n'
            '  "explanation": "Removed filler words.",\n'
            '  "original_quality_score": 60,\n'
            '  "optimized_quality_score": 80\n'
            '}'
        )

        mock_completions = AsyncMock()
        mock_completions.choices = [mock_choice]
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_completions)

        payload = {
            "prompt": "Please optimize this very long prompt text here.",  # len=46 -> 11 tokens
            "optimization_mode": "save_tokens"
        }

        response = await client.post("/api/v1/optimize", json=payload)
        assert response.status_code == 200
        res_data = response.json()
        assert res_data["optimized_prompt"] == "Optimize long text."  # len=19 -> 4 tokens
        result = res_data["optimizationResult"]
        assert result["optimizationAccepted"] is True
        assert result["status"] == "Accepted"
        assert result["originalTokens"] == 12
        assert result["optimizedTokens"] == 4
        assert result["tokenDelta"] == -8


@pytest.mark.asyncio
async def test_optimize_remains_unchanged(client):
    with patch("app.services.groq.AsyncGroq") as mock_async_groq:
        mock_instance = mock_async_groq.return_value

        mock_choice = AsyncMock()
        mock_choice.message = AsyncMock()
        mock_choice.message.content = (
            '{\n'
            '  "optimized_prompt": "Hello world",\n'
            '  "explanation": "No changes needed.",\n'
            '  "original_quality_score": 80,\n'
            '  "optimized_quality_score": 80\n'
            '}'
        )

        mock_completions = AsyncMock()
        mock_completions.choices = [mock_choice]
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_completions)

        payload = {
            "prompt": "Hello world",  # 2 tokens
            "optimization_mode": "save_tokens"
        }

        response = await client.post("/api/v1/optimize", json=payload)
        assert response.status_code == 200
        res_data = response.json()
        assert res_data["optimized_prompt"] == "Hello world"
        result = res_data["optimizationResult"]
        assert result["optimizationAccepted"] is True
        assert result["status"] == "Accepted"


@pytest.mark.asyncio
async def test_optimize_longer_rejected_by_efficiency(client):
    with patch("app.services.groq.AsyncGroq") as mock_async_groq:
        mock_instance = mock_async_groq.return_value

        mock_choice = AsyncMock()
        mock_choice.message = AsyncMock()
        mock_choice.message.content = (
            '{\n'
            '  "optimized_prompt": "Please act as a helpful assistant and do hello",\n'
            '  "explanation": "Expanded layout.",\n'
            '  "original_quality_score": 90,\n'
            '  "optimized_quality_score": 92\n'
            '}'
        )

        mock_completions = AsyncMock()
        mock_completions.choices = [mock_choice]
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_completions)

        payload = {
            "prompt": "Hello",  # len=5 -> 1 token. original efficiency = 90 / 1 = 90
            # optimized: len=49 -> 12 tokens. optimized efficiency = 92 / 12 = 7.66
            "optimization_mode": "balanced"
        }

        response = await client.post("/api/v1/optimize", json=payload)
        assert response.status_code == 200
        res_data = response.json()
        result = res_data["optimizationResult"]
        assert result["optimizationAccepted"] is False
        assert result["status"] == "Rejected"
        # 1 token -> 11 tokens is 1000% token increase
        assert "1000% token increase" in result["reason"]
        assert result["recommendation"] == "Use Original Prompt"


