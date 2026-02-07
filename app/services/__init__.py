"""
Maestro AI Server - 服务模块
@author LJY
"""

from app.services.defect_service import DefectService, get_defect_service
from app.services.text_service import TextService, get_text_service

__all__ = [
    "DefectService",
    "TextService",
    "get_defect_service",
    "get_text_service",
]
