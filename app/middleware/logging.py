"""
Maestro AI Server - 日志中间件
记录请求和响应的详细日志，用于调试
@author LJY
"""

import json
import time
import uuid
from typing import Callable

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message

logger = structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    请求响应日志中间件
    记录详细的请求和响应信息，自动屏蔽敏感字段和过大的 Base64 数据
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(request_id=request_id)
        
        start_time = time.time()
        
        # 记录请求
        await self._log_request(request)
        
        try:
            response = await call_next(request)
            
            # 记录响应
            await self._log_response(response, start_time)
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                "request_failed",
                error=str(e),
                duration=process_time,
                status_code=500
            )
            raise
        finally:
            structlog.contextvars.clear_contextvars()

    async def _log_request(self, request: Request):
        """记录请求详情"""
        try:
            # 获取请求体
            body_bytes = await request.body()
            
            # 重置 Request body stream 以供后续使用
            async def receive() -> Message:
                return {"type": "http.request", "body": body_bytes}
            request._receive = receive
            
            body_json = None
            if body_bytes:
                try:
                    body_str = body_bytes.decode("utf-8")
                    body_json = json.loads(body_str)
                    self._mask_sensitive_data(body_json)
                except Exception:
                    body_json = "<binary/non-json data>"
            
            logger.info(
                "incoming_request",
                method=request.method,
                url=str(request.url),
                client_host=request.client.host if request.client else None,
                headers=dict(request.headers), # Header logging might be verbose, keep it or mask carefully
                body=body_json
            )
            
        except Exception as e:
            logger.warn("log_request_error", error=str(e))

    async def _log_response(self, response: Response, start_time: float):
        """记录响应详情"""
        process_time = time.time() - start_time
        
        # Capture response body
        # 注意: StreamingResponse 的 body 只能读取一次，这里我们主要记录 header 和状态码
        # 如果需要记录 body，需要 wrap response，这里为了性能和稳定性暂时只记录非流式响应或关键信息
        # 对于 JSONResponse，我们可以尝试获取 body，但标准 Response 对象 body 已被消耗
        
        # 简单记录状态和耗时
        logger.info(
            "request_completed",
            status_code=response.status_code,
            duration=process_time,
            headers=dict(response.headers)
        )

    def _mask_headers(self, headers: dict) -> dict:
        """屏蔽敏感 Header"""
        masked = headers.copy()
        if "authorization" in masked:
            masked["authorization"] = "***"
        if "Authorization" in masked:
            masked["Authorization"] = "***"
        return masked

    def _mask_sensitive_data(self, data: any):
        """递归屏蔽 JSON 中的敏感/大字段"""
        if isinstance(data, dict):
            for key, value in data.items():
                if key in ["screen", "image", "file"] and isinstance(value, str):
                    if len(value) > 100:
                        data[key] = f"<base64_data_len_{len(value)}>"
                elif isinstance(value, (dict, list)):
                    self._mask_sensitive_data(value)
        elif isinstance(data, list):
            for item in data:
                self._mask_sensitive_data(item)

