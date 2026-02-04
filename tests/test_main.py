from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
import pytest
from app.main import app
from app.models import Defect

# We need to mock the AIService init and methods
@pytest.fixture
def mock_ai_service():
    with patch("app.main.AIService") as MockService:
        instance = MockService.return_value
        instance.find_defects = AsyncMock()
        instance.extract_text = AsyncMock()
        yield instance

def test_health_check():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_find_defects(mock_ai_service):
    mock_ai_service.find_defects.return_value = [
        Defect(category="ASSERTION_FAILED", reasoning="Button not visible")
    ]
    
    with TestClient(app) as client:
        # Trigger the lifespan event
        response = client.post(
            "/v2/find-defects",
            json={"assertion": "Button is visible", "screen": "base64encodedimage"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["defects"]) == 1
        assert data["defects"][0]["category"] == "ASSERTION_FAILED"
        assert data["defects"][0]["reasoning"] == "Button not visible"
        
        mock_ai_service.find_defects.assert_called_once()

def test_extract_text(mock_ai_service):
    mock_ai_service.extract_text.return_value = "$12.99"
    
    with TestClient(app) as client:
        response = client.post(
            "/v2/extract-text",
            json={"query": "Price?", "screen": "base64encodedimage"}
        )
        
        assert response.status_code == 200
        assert response.json() == {"text": "$12.99"}
        
        mock_ai_service.extract_text.assert_called_once()
