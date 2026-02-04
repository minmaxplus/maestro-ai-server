import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.services import AIService
from langchain_core.messages import AIMessage

@pytest.fixture
def mock_env():
    with patch.dict("os.environ", {
        "OPENAI_API_KEY": "test_key", 
        "OPENAI_API_BASE": "test_base",
        "AI_MODEL_NAME": "test_model"
    }):
        yield

@pytest.fixture
def mock_langchain(mock_env):
    with patch("app.services.ChatOpenAI") as MockLLM:
        llm_instance = MockLLM.return_value
        llm_instance.ainvoke = AsyncMock()
        yield llm_instance

@pytest.mark.asyncio
async def test_find_defects_valid(mock_langchain):
    ai_service = AIService()
    
    # 模拟 LLM 响应
    mock_langchain.ainvoke.return_value = AIMessage(content='{"is_valid": true, "reasoning": "ok"}')
    
    defects = await ai_service.find_defects("screen_data", "assertion")
    
    assert len(defects) == 0
    mock_langchain.ainvoke.assert_called_once()

@pytest.mark.asyncio
async def test_find_defects_invalid(mock_langchain):
    ai_service = AIService()
    
    # 模拟 LLM 响应
    mock_langchain.ainvoke.return_value = AIMessage(content='{"is_valid": false, "reasoning": "bad", "category": "VISUAL"}')
    
    defects = await ai_service.find_defects("screen_data", "assertion")
    
    assert len(defects) == 1
    assert defects[0].category == "VISUAL"
    assert defects[0].reasoning == "bad"

@pytest.mark.asyncio
async def test_extract_text(mock_langchain):
    ai_service = AIService()
    
    # 模拟 LLM 响应
    mock_langchain.ainvoke.return_value = AIMessage(content='{"text": "extracted text"}')
    
    text = await ai_service.extract_text("screen_data", "query")
    
    assert text == "extracted text"
    mock_langchain.ainvoke.assert_called_once()
