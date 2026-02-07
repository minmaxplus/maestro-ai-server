"""
Maestro AI Server - 文本提取相关 Schema 定义
@author LJY
"""

from pydantic import BaseModel, Field


class ExtractTextRequest(BaseModel):
    """文本提取请求"""
    screen: bytes = Field(description="屏幕截图 (Base64 编码)")
    query: str = Field(description="查询条件，描述需要提取的文本")


class ExtractTextResponse(BaseModel):
    """文本提取响应"""
    text: str = Field(description="提取的文本内容")
