"""
Maestro AI Server - 缺陷检测相关 Schema 定义
@author LJY
"""

from pydantic import BaseModel, Field


class Defect(BaseModel):
    """缺陷信息"""
    category: str = Field(description="缺陷类别，如 ASSERTION_FAILED, UI_BUG 等")
    reasoning: str = Field(description="缺陷原因说明")


class FindDefectsRequest(BaseModel):
    """缺陷检测请求"""
    screen: bytes = Field(description="屏幕截图 (Base64 编码)")
    assertion: str | None = Field(
        default=None,
        description="可选的断言条件，用于 assertWithAI 命令"
    )


class FindDefectsResponse(BaseModel):
    """缺陷检测响应"""
    defects: list[Defect] = Field(
        default_factory=list,
        description="检测到的缺陷列表"
    )
