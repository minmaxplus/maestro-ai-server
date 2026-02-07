"""
Maestro AI Server - 文本提取 Agent
使用 LangChain v1 create_agent 和结构化输出
@author LJY
"""

import structlog
from pydantic import BaseModel, Field

from app.agents.base import BaseAgent
from app.agents.prompts import (
    TEXT_EXTRACTION_SYSTEM_PROMPT,
    TEXT_EXTRACTION_USER_PROMPT,
)

logger = structlog.get_logger()


class TextExtractionOutput(BaseModel):
    """文本提取结构化输出"""
    text: str = Field(default="", description="提取的文本内容")


class TextExtractionAgent(BaseAgent):
    """文本提取 Agent"""
    
    def __init__(self, llm):
        super().__init__(llm, TextExtractionOutput)
    
    def get_prompt(self, query: str, **kwargs) -> str:
        prompt = f"{TEXT_EXTRACTION_SYSTEM_PROMPT}\n\n{TEXT_EXTRACTION_USER_PROMPT.format(query=query)}"
        return prompt
    
    async def extract(self, image_data: bytes, query: str) -> str:
        """
        从屏幕截图中提取文本
        
        Args:
            image_data: 原始图像字节
            query: 查询条件
        
        Returns:
            提取的文本
        """
        result: TextExtractionOutput = await self.invoke(image_data, query=query)
        
        logger.info(
            "text_extracted",
            text_length=len(result.text),
            has_content=bool(result.text)
        )
        
        return result.text
