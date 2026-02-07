"""
Maestro AI Server - 缺陷检测 API 端点
@author LJY
"""

import structlog
from fastapi import APIRouter

from app.api.deps import ApiKeyDep, DefectServiceDep
from app.schemas import FindDefectsRequest, FindDefectsResponse

logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/find-defects",
    response_model=FindDefectsResponse,
    summary="检测屏幕截图中的缺陷",
    description="分析屏幕截图，识别 UI 缺陷。可选传入断言条件进行验证。"
)
async def find_defects(
    request: FindDefectsRequest,
    api_key: ApiKeyDep,
    service: DefectServiceDep,
) -> FindDefectsResponse:
    """
    检测屏幕截图中的缺陷
    
    - **screen**: Base64 编码的屏幕截图
    - **assertion**: 可选的断言条件 (用于 assertWithAI 命令)
    
    返回检测到的缺陷列表，每个缺陷包含类别和推理说明。
    """
    logger.info(
        "api_find_defects",
        has_assertion=request.assertion is not None
    )
    
    defects = await service.find_defects(
        screen=request.screen,
        assertion=request.assertion
    )
    
    return FindDefectsResponse(defects=defects)
