"""
Maestro AI Server - 文本提取服务
@author LJY
"""

import structlog

from app.agents import TextExtractionAgent
from app.core.llm import create_llm_client
from app.utils import decode_byte_array_image

logger = structlog.get_logger()


class TextService:
    """文本提取服务"""
    
    def __init__(self):
        llm = create_llm_client()
        self.agent = TextExtractionAgent(llm)
    
    async def extract_text(self, screen: list[int], query: str) -> str:
        """
        从屏幕截图中提取文本
        
        Args:
            screen: 字节数组格式的屏幕截图
            query: 查询条件
        
        Returns:
            提取的文本
        """
        # 将有符号字节数组转换为 bytes
        image_data = decode_byte_array_image(screen)
        
        logger.info(
            "extract_text_start",
            query=query,
            image_size=len(image_data)
        )
        
        text = await self.agent.extract(image_data, query)
        
        logger.info(
            "extract_text_complete",
            text_length=len(text)
        )
        
        return text


# 服务单例
_text_service: TextService | None = None


def get_text_service() -> TextService:
    """获取文本提取服务单例"""
    global _text_service
    if _text_service is None:
        _text_service = TextService()
    return _text_service
