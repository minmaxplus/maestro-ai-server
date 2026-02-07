"""
Maestro AI Server - 文本提取 API 端点
@author LJY
"""

import structlog
from fastapi import APIRouter

from app.api.deps import ApiKeyDep, TextServiceDep
from app.schemas import ExtractTextRequest, ExtractTextResponse

logger = structlog.get_logger()

router = APIRouter()


@router.post(
    "/extract-text",
    response_model=ExtractTextResponse,
    summary="从屏幕截图中提取文本",
    description="根据查询条件从屏幕截图中提取指定的文本内容。"
)
async def extract_text(
    request: ExtractTextRequest,
    api_key: ApiKeyDep,
    service: TextServiceDep,
) -> ExtractTextResponse:
    """
    从屏幕截图中提取文本
    
    - **screen**: Base64 编码的屏幕截图
    - **query**: 查询条件，描述需要提取的文本
    
    返回提取的文本内容。
    """
    logger.info(
        "api_extract_text",
        query=request.query
    )
    
    text = await service.extract_text(
        screen=request.screen,
        query=request.query
    )
    
    return ExtractTextResponse(text=text)
