"""
Maestro AI Server - 测试配置
@author LJY
"""

import pytest


@pytest.fixture
def mock_image_base64() -> bytes:
    """模拟 Base64 编码的图像"""
    # 最小有效 PNG 图像的 Base64
    return b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


@pytest.fixture
def mock_defect_response() -> str:
    """模拟缺陷检测 LLM 响应"""
    return '''```json
{
  "defects": [
    {
      "category": "ASSERTION_FAILED",
      "reasoning": "页面未显示登录按钮"
    }
  ]
}
```'''


@pytest.fixture
def mock_text_response() -> str:
    """模拟文本提取 LLM 响应"""
    return '''```json
{
  "text": "欢迎使用 Maestro"
}
```'''


@pytest.fixture
def mock_empty_defects_response() -> str:
    """模拟无缺陷的 LLM 响应"""
    return '''```json
{
  "defects": []
}
```'''
