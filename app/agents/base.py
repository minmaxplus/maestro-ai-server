"""
Maestro AI Server - Agent 基类
提供通用的 LLM 调用和图像处理能力
@author LJY
"""

import json
import re
from abc import ABC, abstractmethod
from typing import Any

import structlog
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.config import get_settings
from app.core import LLMError
from app.utils.image import encode_image_to_base64, get_image_mime_type, resize_image_if_needed

logger = structlog.get_logger()


class BaseAgent(ABC):
    """Agent 基类"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.settings = get_settings()
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        pass
    
    @abstractmethod
    def get_user_prompt(self, **kwargs) -> str:
        """获取用户提示词"""
        pass
    
    @abstractmethod
    def parse_response(self, response: str) -> Any:
        """解析 LLM 响应"""
        pass
    
    def _create_image_content(self, image_data: bytes) -> dict:
        """创建图像内容块"""
        # 缩放图像以避免超出限制
        processed_image = resize_image_if_needed(image_data)
        base64_image = encode_image_to_base64(processed_image)
        mime_type = get_image_mime_type(processed_image)
        
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:{mime_type};base64,{base64_image}",
                "detail": "high"
            }
        }
    
    def _extract_json_from_response(self, response: str) -> dict:
        """从 LLM 响应中提取 JSON"""
        # 尝试直接解析
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # 尝试从 markdown 代码块中提取
        json_pattern = r"```(?:json)?\s*([\s\S]*?)```"
        matches = re.findall(json_pattern, response)
        
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue
        
        raise LLMError(f"无法从响应中解析 JSON: {response[:200]}...")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(LLMError),
        reraise=True
    )
    async def invoke(self, image_data: bytes, **kwargs) -> Any:
        """
        调用 LLM 进行推理
        包含自动重试机制
        """
        try:
            system_message = SystemMessage(content=self.get_system_prompt())
            
            user_prompt = self.get_user_prompt(**kwargs)
            image_content = self._create_image_content(image_data)
            
            user_message = HumanMessage(content=[
                {"type": "text", "text": user_prompt},
                image_content
            ])
            
            logger.info(
                "invoking_llm",
                agent=self.__class__.__name__,
                model=self.llm.model_name,
            )
            
            response = await self.llm.ainvoke([system_message, user_message])
            response_text = response.content
            
            logger.debug(
                "llm_response",
                agent=self.__class__.__name__,
                response_length=len(response_text),
            )
            
            return self.parse_response(response_text)
            
        except LLMError:
            raise
        except Exception as e:
            logger.error(
                "llm_invoke_error",
                agent=self.__class__.__name__,
                error=str(e),
            )
            raise LLMError(f"LLM 调用失败: {e}")
