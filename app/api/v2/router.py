"""
Maestro AI Server - V2 API 路由聚合
@author LJY
"""

from fastapi import APIRouter

from app.api.v2 import defects, extract

router = APIRouter(prefix="/v2", tags=["v2"])

router.include_router(defects.router)
router.include_router(extract.router)
