"""
Maestro AI Server - Middleware Tests
@author LJY
"""

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from app.middleware.logging import LoggingMiddleware


@pytest.mark.asyncio
async def test_logging_middleware():
    """Test that logging middleware allows requests to pass through and logs"""
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)
    
    @app.post("/test")
    async def test_endpoint(data: dict):
        return {"received": data}
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test valid JSON
        response = await client.post("/test", json={"key": "value"})
        assert response.status_code == 200
        assert response.json() == {"received": {"key": "value"}}
        
        # Test body with "screen" key (should be masked in logs, but here we just check pass-through)
        response = await client.post("/test", json={"screen": "base64data", "other": "data"})
        assert response.status_code == 200
        assert response.json() == {"received": {"screen": "base64data", "other": "data"}}
