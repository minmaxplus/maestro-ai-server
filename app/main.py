"""
Maestro AI Server - FastAPI 应用主入口
提供 AI 断言验证和文本提取服务
@author LJY
"""

import os
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v2 import router as v2_router
from app.config import get_settings
from app.core import LLMError, MaestroAIError

# 配置结构化日志
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    settings = get_settings()
    
    # 启动时配置 LangSmith
    if settings.langchain_tracing_v2:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = settings.langchain_endpoint
        os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
        logger.info("langsmith_tracing_enabled", project=settings.langchain_project)
    
    logger.info(
        "application_startup",
        llm_provider=settings.llm_provider.value,
        model=settings.current_model,
    )
    
    yield
    
    logger.info("application_shutdown")


app = FastAPI(
    title="Maestro AI Server",
    description="基于 LangChain 的 AI 断言验证和文本提取服务",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(MaestroAIError)
async def maestro_ai_exception_handler(
    request: Request,
    exc: MaestroAIError
) -> JSONResponse:
    """处理自定义异常"""
    logger.error("maestro_ai_error", error=str(exc))
    
    if isinstance(exc, LLMError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": f"AI 服务暂时不可用: {exc}"}
        )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc)}
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """处理未预期的异常"""
    logger.exception("unexpected_error", error=str(exc))
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "服务器内部错误"}
    )


# 注册路由
app.include_router(v2_router)


@app.get("/health", tags=["health"])
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


@app.get("/", tags=["root"])
async def root():
    """根路径"""
    return {
        "service": "Maestro AI Server",
        "version": "0.1.0",
        "docs": "/docs"
    }
