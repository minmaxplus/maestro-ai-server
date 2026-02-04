from typing import List, Optional
from pydantic import BaseModel

class Defect(BaseModel):
    category: str
    reasoning: str

class FindDefectsRequest(BaseModel):
    assertion: Optional[str] = None
    screen: str  # Base64 编码字符串

class FindDefectsResponse(BaseModel):
    defects: List[Defect]

class ExtractTextWithAiRequest(BaseModel):
    query: str
    screen: str  # Base64 编码字符串

class ExtractTextWithAiResponse(BaseModel):
    text: str
