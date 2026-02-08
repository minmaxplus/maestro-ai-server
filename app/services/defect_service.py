"""
Maestro AI Server - 缺陷检测服务
@author LJY
"""

import structlog

from app.agents import DefectDetectionAgent
from app.core.llm import create_llm_client
from app.schemas import Defect
from app.utils import decode_byte_array_image

logger = structlog.get_logger()


class DefectService:
    """缺陷检测服务"""
    
    def __init__(self):
        llm = create_llm_client()
        self.agent = DefectDetectionAgent(llm)
    
    async def find_defects(
        self,
        screen: list[int],
        assertion: str | None = None
    ) -> list[Defect]:
        """
        检测屏幕截图中的缺陷
        
        Args:
            screen: 字节数组格式的屏幕截图 (Maestro CLI 发送的有符号字节数组)
            assertion: 可选的断言条件
        
        Returns:
            检测到的缺陷列表
        """
        # 将有符号字节数组转换为 bytes
        image_data = decode_byte_array_image(screen)
        
        logger.info(
            "find_defects_start",
            has_assertion=assertion is not None,
            image_size=len(image_data)
        )
        
        defects = await self.agent.detect(image_data, assertion)
        
        logger.info(
            "find_defects_complete",
            defect_count=len(defects)
        )
        
        return defects


# 服务单例
_defect_service: DefectService | None = None


def get_defect_service() -> DefectService:
    """获取缺陷检测服务单例"""
    global _defect_service
    if _defect_service is None:
        _defect_service = DefectService()
    return _defect_service
