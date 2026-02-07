"""
Maestro AI Server - API 依赖注入
@author LJY
"""

from typing import Annotated

from fastapi import Depends, Header, HTTPException, status

from app.config import get_settings
from app.services import DefectService, TextService, get_defect_service, get_text_service


async def verify_api_key(
    authorization: Annotated[str | None, Header()] = None
) -> str:
    """
    验证 API Key (Bearer Token)
    与 Maestro Client 兼容
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header"
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format"
        )
    
    # 提取 token (当前仅验证格式，实际可添加更多验证)
    token = authorization[7:]
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty API key"
        )
    
    return token


# 类型别名
ApiKeyDep = Annotated[str, Depends(verify_api_key)]
DefectServiceDep = Annotated[DefectService, Depends(get_defect_service)]
TextServiceDep = Annotated[TextService, Depends(get_text_service)]
