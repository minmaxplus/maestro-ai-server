"""
Maestro AI Server - 缺陷检测 Agent
@author LJY
"""

import structlog

from app.agents.base import BaseAgent
from app.agents.prompts import (
    ASSERTION_SECTION_TEMPLATE,
    DEFECT_DETECTION_SYSTEM_PROMPT,
    DEFECT_DETECTION_USER_PROMPT,
)
from app.schemas import Defect

logger = structlog.get_logger()


class DefectDetectionAgent(BaseAgent):
    """缺陷检测 Agent"""
    
    def get_system_prompt(self) -> str:
        return DEFECT_DETECTION_SYSTEM_PROMPT
    
    def get_user_prompt(self, assertion: str | None = None, **kwargs) -> str:
        if assertion:
            assertion_section = ASSERTION_SECTION_TEMPLATE.format(assertion=assertion)
        else:
            assertion_section = "请检测所有可见的 UI 缺陷和问题。"
        
        return DEFECT_DETECTION_USER_PROMPT.format(assertion_section=assertion_section)
    
    def parse_response(self, response: str) -> list[Defect]:
        """解析缺陷检测响应"""
        data = self._extract_json_from_response(response)
        
        defects = []
        for defect_data in data.get("defects", []):
            defects.append(Defect(
                category=defect_data.get("category", "UNKNOWN"),
                reasoning=defect_data.get("reasoning", "")
            ))
        
        logger.info(
            "defects_detected",
            count=len(defects),
            categories=[d.category for d in defects]
        )
        
        return defects
    
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
        return await self.invoke(image_data, assertion=assertion)
