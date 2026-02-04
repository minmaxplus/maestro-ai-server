import os
import logging
from typing import List, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.models import Defect

logger = logging.getLogger(__name__)

# 定义 LLM 的输出结构
class DefectOutput(BaseModel):
    is_valid: bool = Field(description="如果屏幕截图符合断言，则为 True，否则为 False。")
    reasoning: str = Field(description="解释为什么符合或不符合。")
    category: Optional[str] = Field(description="如果不符合，则为缺陷类别（例如 'ASSERTION_FAILED'）。", default=None)

class ExtractionOutput(BaseModel):
    text: str = Field(description="提取的文本值。")

class AIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_API_BASE")
        model_name = os.getenv("AI_MODEL_NAME", "kimi-k2.5")

        if not api_key:
            logger.warning("OPENAI_API_KEY not set. AI features will fail.")

        self.llm = ChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            openai_api_base=base_url,
            temperature=float(os.getenv("AI_TEMPERATURE", 1.0)),
            max_tokens=2048
        )
        
        self.defect_parser = JsonOutputParser(pydantic_object=DefectOutput)
        self.extraction_parser = JsonOutputParser(pydantic_object=ExtractionOutput)

    async def find_defects(self, screen_base64: str, assertion: Optional[str]) -> List[Defect]:
        if not assertion:
            # TODO: 如果需要，实现通用缺陷查找。
            # 目前，如果没有提供断言，我们假设不需要特定检查或默认为通用检查。
            # 但是，Maestro 通常会为 `assertVisible` 发送断言。
            # 如果 assertion 为空，也许我们只返回空列表？
            return []

        prompt_text = f"""
        You are a QA automation expert. Your task is to verify a UI assertion based on the provided screen image.
        
        Assertion: "{assertion}"
        
        Analyze the image carefully. Does the UI satisfy the assertion?
        If it does, set 'is_valid' to true.
        If it does not, set 'is_valid' to false and provide a clear 'reasoning' and set category to 'ASSERTION_FAILED'.
        
        {self.defect_parser.get_format_instructions()}
        """

        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt_text},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{screen_base64}"},
                },
            ]
        )

        try:
            response = await self.llm.ainvoke([message])
            logger.info(f"LLM Response (find_defects): {response.content}")
            # The response from ChatOpenAI is an AIMessage. We need to parse its content.
            # However, using a parser directly on the output of invoke is cleaner if we use a chain,
            # but here we can just parse the content string.
            
            parsed_result = self.defect_parser.parse(response.content)
            result = DefectOutput(**parsed_result)
            
            if result.is_valid:
                return []
            else:
                return [
                    Defect(
                        category=result.category or "ASSERTION_FAILED",
                        reasoning=result.reasoning
                    )
                ]

        except Exception as e:
            logger.error(f"Error in find_defects: {e}")
            # Fallback or re-raise. For now, return a generic error defect.
            return [Defect(category="AI_ERROR", reasoning=f"Failed to process AI request: {str(e)}")]

    async def extract_text(self, screen_base64: str, query: str) -> str:
        prompt_text = f"""
        You are a helpful assistant that extracts information from UI screenshots.
        
        Query: "{query}"
        
        Analyze the image and extract the text that answers the query.
        Return ONLY the extracted text in the specified JSON format.
        
        {self.extraction_parser.get_format_instructions()}
        """

        message = HumanMessage(
            content=[
                {"type": "text", "text": prompt_text},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{screen_base64}"},
                },
            ]
        )

        try:
            response = await self.llm.ainvoke([message])
            logger.info(f"LLM Response (extract_text): {response.content}")
            parsed_result = self.extraction_parser.parse(response.content)
            result = ExtractionOutput(**parsed_result)
            return result.text
            
        except Exception as e:
            logger.error(f"Error in extract_text: {e}")
            raise e
