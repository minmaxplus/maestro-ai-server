"""
Maestro AI Server - 缺陷检测 API 测试
@author LJY
"""

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

from app.main import app
from app.schemas import Defect


@pytest.fixture
def mock_defect_service():
    """模拟缺陷检测服务"""
    with patch("app.api.v2.defects.DefectServiceDep") as mock:
        service = AsyncMock()
        service.find_defects = AsyncMock(return_value=[
            Defect(category="ASSERTION_FAILED", reasoning="测试失败原因")
        ])
        mock.return_value = service
        yield service


class TestFindDefectsEndpoint:
    """测试 /v2/find-defects 端点"""
    
    @pytest.mark.asyncio
    async def test_find_defects_without_auth(self, mock_image_base64: bytes):
        """测试缺少认证头"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/v2/find-defects",
                json={"screen": mock_image_base64.decode()}
            )
            assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_find_defects_invalid_auth(self, mock_image_base64: bytes):
        """测试无效的认证格式"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/v2/find-defects",
                headers={"Authorization": "InvalidFormat"},
                json={"screen": mock_image_base64.decode()}
            )
            assert response.status_code == 401


class TestExtractTextEndpoint:
    """测试 /v2/extract-text 端点"""
    
    @pytest.mark.asyncio
    async def test_extract_text_without_auth(self, mock_image_base64: bytes):
        """测试缺少认证头"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/v2/extract-text",
                json={"screen": mock_image_base64.decode(), "query": "提取标题"}
            )
            assert response.status_code == 401


class TestHealthEndpoint:
    """测试健康检查端点"""
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """测试健康检查"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            assert response.json() == {"status": "healthy"}
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """测试根路径"""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")
            assert response.status_code == 200
            data = response.json()
            assert data["service"] == "Maestro AI Server"
