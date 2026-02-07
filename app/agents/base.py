"""
Maestro AI Server - Agent 基类
使用 LangChain v1 的 create_agent API 和结构化输出
@author LJY
"""

import base64
from abc import ABC, abstractmethod
from typing import Any, TypeVar

import structlog
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.config import get_settings
from app.utils.image import encode_image_to_base64, get_image_mime_type, resize_image_if_needed

logger = structlog.get_logger()

T = TypeVar("T", bound=BaseModel)


class BaseAgent(ABC):
    """
    Agent 基类
    使用 LangChain v1 的 create_agent 和 ProviderStrategy 结构化输出
    """
    
    def __init__(self, llm: ChatOpenAI, output_schema: type[T]):
        self.llm = llm
        self.output_schema = output_schema
        self.settings = get_settings()
        
        # 创建带结构化输出的 Agent
        self.agent = create_agent(
            model=llm,
            tools=[],  # 纯视觉分析，无需工具
            response_format=ProviderStrategy(output_schema)
        )
    
    @abstractmethod
    def get_prompt(self, **kwargs) -> str:
        """生成用户提示词"""
        pass
    
    def _create_image_message(self, image_data: bytes) -> dict:
        """创建包含图像的消息"""
        # 缩放图像以避免超出限制
        processed_image = resize_image_if_needed(image_data)
        base64_image = encode_image_to_base64(processed_image)
        mime_type = get_image_mime_type(processed_image)
        
        return {
            "type": "image",
            "source_type": "base64",
            "data": base64_image,
            "mime_type": mime_type,
        }
    
    async def invoke(self, image_data: bytes, **kwargs) -> T:
        """
        调用 Agent 进行推理
        返回结构化输出
        """
        prompt = self.get_prompt(**kwargs)
        image_msg = self._create_image_message(image_data)
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    image_msg
                ]
            }
        ]
        
        logger.info(
            "invoking_agent",
            agent=self.__class__.__name__,
            model=self.llm.model_name,
        )
        
        result = await self.agent.ainvoke({"messages": messages})
        
        # LangChain v1 的结构化响应在 structured_response 键中
        structured_response = result.get("structured_response")
        
        logger.debug(
            "agent_response",
            agent=self.__class__.__name__,
            response_type=type(structured_response).__name__,
        )
        
        return structured_response
