"""
Maestro AI Server 配置管理模块
使用 Pydantic Settings 从环境变量加载配置
@author LJY
"""

from enum import Enum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """支持的 LLM 提供商"""
    OPENAI = "openai"
    KIMI = "kimi"


class Settings(BaseSettings):
    """应用配置"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # LLM 配置
    llm_provider: LLMProvider = Field(
        default=LLMProvider.KIMI,
        description="LLM 提供商"
    )
    
    # Kimi 配置
    kimi_api_key: str = Field(default="", description="Kimi API Key")
    kimi_api_base: str = Field(
        default="https://api.moonshot.cn/v1",
        description="Kimi API Base URL"
    )
    kimi_model: str = Field(
        default="moonshot-v1-vision",
        description="Kimi 模型名称"
    )
    
    # OpenAI 配置
    openai_api_key: str = Field(default="", description="OpenAI API Key")
    openai_model: str = Field(default="gpt-4o", description="OpenAI 模型名称")
    
    # 重试配置
    max_retries: int = Field(default=3, description="最大重试次数")
    retry_initial_delay: float = Field(default=1.0, description="重试初始延迟(秒)")
    retry_backoff_factor: float = Field(default=2.0, description="重试退避因子")
    
    # LangSmith 配置
    langchain_tracing_v2: bool = Field(default=True, description="启用 LangSmith 追踪")
    langchain_endpoint: str = Field(
        default="https://api.smith.langchain.com",
        description="LangSmith API 端点"
    )
    langchain_api_key: str = Field(default="", description="LangSmith API Key")
    langchain_project: str = Field(
        default="maestro-ai-server",
        description="LangSmith 项目名称"
    )
    
    # 服务配置
    port: int = Field(default=8000, description="服务端口")
    log_level: str = Field(default="INFO", description="日志级别")
    
    @property
    def current_api_key(self) -> str:
        """获取当前 LLM 提供商的 API Key"""
        if self.llm_provider == LLMProvider.KIMI:
            return self.kimi_api_key
        return self.openai_api_key
    
    @property
    def current_model(self) -> str:
        """获取当前 LLM 提供商的模型名称"""
        if self.llm_provider == LLMProvider.KIMI:
            return self.kimi_model
        return self.openai_model
    
    @property
    def current_api_base(self) -> str | None:
        """获取当前 LLM 提供商的 API Base URL"""
        if self.llm_provider == LLMProvider.KIMI:
            return self.kimi_api_base
        return None  # OpenAI 使用默认 URL


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()
