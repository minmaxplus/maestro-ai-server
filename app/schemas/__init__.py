"""
Maestro AI Server - Schema 模块
@author LJY
"""

from app.schemas.defects import Defect, FindDefectsRequest, FindDefectsResponse
from app.schemas.extract import ExtractTextRequest, ExtractTextResponse

__all__ = [
    "Defect",
    "FindDefectsRequest",
    "FindDefectsResponse",
    "ExtractTextRequest",
    "ExtractTextResponse",
]
