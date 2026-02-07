"""
Maestro AI Server - LLM 客户端工厂
支持 Kimi 和 OpenAI
@author LJY
"""

from langchain_openai import ChatOpenAI

from app.config import LLMProvider, Settings, get_settings


def create_llm_client(settings: Settings | None = None) -> ChatOpenAI:
    """
    创建 LLM 客户端
    Kimi API 兼容 OpenAI 格式，使用 ChatOpenAI 配合自定义 base_url
    """
    if settings is None:
        settings = get_settings()
    
    if settings.llm_provider == LLMProvider.KIMI:
        return ChatOpenAI(
            model=settings.kimi_model,
            api_key=settings.kimi_api_key,
            base_url=settings.kimi_api_base,
            max_retries=settings.max_retries,
        )
    else:
        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            max_retries=settings.max_retries,
        )
