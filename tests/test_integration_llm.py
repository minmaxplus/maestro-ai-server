import pytest
import os
from dotenv import load_dotenv
from app.services import AIService

# Load environment variables from .env
load_dotenv()

# 50x50 Red Square PNG Base64
RED_SQUARE_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAIAAACRXR/mAAAAQ0lEQVR4nO3OMQ0AMAwDsPAnvRHonxyWDMB5yaD+QEtLS0tLa0N/oKWlpaWltaE/0NLS0tLS2tAfaGlpaWlpbegPTh97K7rEaOcNTQAAAABJRU5ErkJggg=="

@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
async def test_real_llm_extract_text():
    """
    Integration test that calls the real LLM endpoint to extract text (or description) from an image.
    Note: Requires a valid API Key in .env
    """
    service = AIService()
    
    # Kimi / GLM-4V are smart enough to describe a red pixel or answer "What color is this?"
    query = "What color is this image? Reply with just the color name."
    
    try:
        text = await service.extract_text(RED_SQUARE_BASE64, query)
        print(f"\n[Real LLM Response] Extract Text: {text}")
        
        # We expect some response. Exact matching is hard with LLMs, but it shouldn't be empty.
        assert text is not None
        assert len(text) > 0
        # Typical answer might be "Red" or "Red color"
        assert "red" in text.lower()
        
    except Exception as e:
        pytest.fail(f"Real LLM call failed: {e}")

@pytest.mark.asyncio
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
async def test_real_llm_find_defects():
    """
    Integration test that calls the real LLM endpoint to verify an assertion.
    """
    service = AIService()
    
    # Assertion: "The image is red" -> Should be Valid
    assertion = "The image is red"
    
    try:
        defects = await service.find_defects(RED_SQUARE_BASE64, assertion)
        print(f"\n[Real LLM Response] Find Defects (Valid): {defects}")
        assert len(defects) == 0  # Should be empty for valid assertion
        
    except Exception as e:
        pytest.fail(f"Real LLM call failed (Valid Case): {e}")

    # Assertion: "The image is blue" -> Should be Invalid
    assertion_invalid = "The image is blue"
    try:
        defects = await service.find_defects(RED_SQUARE_BASE64, assertion_invalid)
        print(f"\n[Real LLM Response] Find Defects (Invalid): {defects}")
        
        assert len(defects) > 0 # Should return a defect
        assert defects[0].category is not None
        assert "blue" in defects[0].reasoning.lower() or "red" in defects[0].reasoning.lower()
        
    except Exception as e:
        pytest.fail(f"Real LLM call failed (Invalid Case): {e}")
