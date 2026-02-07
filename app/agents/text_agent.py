"""
Maestro AI Server - 文本提取 Agent
@author LJY
"""

import structlog

from app.agents.base import BaseAgent
from app.agents.prompts import (
    TEXT_EXTRACTION_SYSTEM_PROMPT,
    TEXT_EXTRACTION_USER_PROMPT,
)

logger = structlog.get_logger()


class TextExtractionAgent(BaseAgent):
    """文本提取 Agent"""
    
    def get_system_prompt(self) -> str:
        return TEXT_EXTRACTION_SYSTEM_PROMPT
    
    def get_user_prompt(self, query: str, **kwargs) -> str:
        return TEXT_EXTRACTION_USER_PROMPT.format(query=query)
    
    def parse_response(self, response: str) -> str:
        """解析文本提取响应"""
        data = self._extract_json_from_response(response)
        text = data.get("text", "")
        
        logger.info(
            "text_extracted",
            text_length=len(text),
            has_content=bool(text)
        )
        
        return text
    
    async def extract(self, image_data: bytes, query: str) -> str:
        """
        从屏幕截图中提取文本
        
        Args:
            image_data: 原始图像字节
            query: 查询条件
        
        Returns:
            提取的文本
        """
        return await self.invoke(image_data, query=query)
