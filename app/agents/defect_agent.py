"""
Maestro AI Server - 缺陷检测 Agent
使用 LangChain v1 create_agent 和结构化输出
@author LJY
"""

import structlog
from pydantic import BaseModel, Field

from app.agents.base import BaseAgent
from app.agents.prompts import (
    ASSERTION_SECTION_TEMPLATE,
    DEFECT_DETECTION_SYSTEM_PROMPT,
    DEFECT_DETECTION_USER_PROMPT,
)
from app.schemas import Defect

logger = structlog.get_logger()


class DefectDetectionOutput(BaseModel):
    """缺陷检测结构化输出"""
    defects: list[Defect] = Field(
        default_factory=list,
        description="检测到的缺陷列表"
    )


class DefectDetectionAgent(BaseAgent):
    """缺陷检测 Agent"""
    
    def __init__(self, llm):
        super().__init__(llm, DefectDetectionOutput)
    
    def get_prompt(self, assertion: str | None = None, **kwargs) -> str:
        if assertion:
            assertion_section = ASSERTION_SECTION_TEMPLATE.format(assertion=assertion)
        else:
            assertion_section = "请检测所有可见的 UI 缺陷和问题。"
        
        prompt = f"{DEFECT_DETECTION_SYSTEM_PROMPT}\n\n{DEFECT_DETECTION_USER_PROMPT.format(assertion_section=assertion_section)}"
        return prompt
    
    async def detect(
        self,
        image_data: bytes,
        assertion: str | None = None
    ) -> list[Defect]:
        """
        检测屏幕截图中的缺陷
        
        Args:
            image_data: 原始图像字节
            assertion: 可选的断言条件
        
        Returns:
            检测到的缺陷列表
        """
        result: DefectDetectionOutput = await self.invoke(image_data, assertion=assertion)
        
        logger.info(
            "defects_detected",
            count=len(result.defects),
            categories=[d.category for d in result.defects]
        )
        
        return result.defects
