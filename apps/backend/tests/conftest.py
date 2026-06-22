import pytest
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.main import app


@pytest.fixture(autouse=True)
def setup_test_env():
    # Force settings for testing phase
    settings.GROQ_API_KEY = "gsk_test_api_key_mocked"
    settings.ENV = "testing"
    settings.CORS_ORIGINS = '["*"]'


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest.fixture
def mock_groq_response():
    return {
        "choices": [
            {
                "message": {
                    "content": '{\n  "optimized_prompt": "Act as an expert FastAPI developer. Guide the user step-by-step on writing a web server.",\n  "explanation": "- Added developer persona\\n- Added step-by-step constraint"\n}'
                }
            }
        ]
    }
