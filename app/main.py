import logging
import os
import sys
import json
import time

from dotenv import load_dotenv
load_dotenv()

from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.concurrency import iterate_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from app.models import (
    FindDefectsRequest,
    FindDefectsResponse,
    ExtractTextWithAiRequest,
    ExtractTextWithAiResponse,
)
from app.services import AIService
from contextlib import asynccontextmanager

# --- Logging Configuration ---
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "maestro_server.log")

# Create a custom logger
logger = logging.getLogger("maestro_ai_server")
logger.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Console Handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File Handler (Rotating)
file_handler = RotatingFileHandler(
    LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Ensure third-party libraries don't propagate too noisily if not desired,
# but usually allowing them to root is fine.
# We set the level for uvicorn access logs to avoid duplicates if we log requests ourselves,
# usually uvicorn logs are fine to keep.

# Helper to truncate large fields
def truncate_sensitive_data(data: dict) -> dict:
    """Recursively truncate 'screen' fields in the log data."""
    if not isinstance(data, dict):
        return data
    
    cleaned = {}
    for k, v in data.items():
        if k == "screen" and isinstance(v, str) and len(v) > 100:
            cleaned[k] = v[:50] + "...[TRUNCATED_BASE64]..."
        elif isinstance(v, dict):
            cleaned[k] = truncate_sensitive_data(v)
        elif isinstance(v, list):
            if len(v) > 50:
                 cleaned[k] = f"List[{len(v)}] (TRUNCATED)"
            else:
                 cleaned[k] = [truncate_sensitive_data(i) if isinstance(i, dict) else i for i in v]
        else:
            cleaned[k] = v
    return cleaned

ai_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global ai_service
    logger.info("Initializing AI Service...")
    try:
        ai_service = AIService()
        logger.info("AI Service initialized successfully.")
    except Exception as e:
        logger.exception(f"Failed to initialize AI Service: {e}")
    yield
    logger.info("Shutting down AI Service...")

app = FastAPI(lifespan=lifespan)

# --- Middleware for Logging ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # 1. Capture Request Body
    # We need to read the body, then put it back for the endpoint to use.
    request_body = None
    try:
        body_bytes = await request.body()
        if body_bytes:
            try:
                # Try parsing as JSON to truncate sensitive fields
                json_body = json.loads(body_bytes)
                request_body = truncate_sensitive_data(json_body)
            except json.JSONDecodeError:
                # Fallback for non-JSON or weird encoding
                request_body = f"Raw/Binary: {len(body_bytes)} bytes"
        
        # Restore the body so the route handler can read it
        async def receive():
            return {"type": "http.request", "body": body_bytes}
        request._receive = receive
        
    except Exception as e:
        logger.error(f"Failed to capture request body: {e}")

    logger.info(f"Incoming Request: {request.method} {request.url}")
    logger.info(f"Client Host: {request.client.host if request.client else 'Unknown'}")
    logger.info(f"Headers: {json.dumps(dict(request.headers), ensure_ascii=False)}")
    if request_body:
        logger.info(f"Request Body: {json.dumps(request_body, ensure_ascii=False)}")

    # 2. Process Request
    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception(f"Request processing failed: {e}")
        raise e

    # 3. Capture Response Body
    # Consuming the response body is tricky because it's an iterator.
    # We read it into memory, log it, then create a new Response.
    response_body = b""
    try:
        # iterate_in_threadpool is used for StreamingResponse, 
        # but for standard responses we can just consume the iterator.
        async for chunk in response.body_iterator:
            response_body += chunk
        
        # Log Response
        duration = time.time() - start_time
        logger.info(f"Response Status: {response.status_code} (Duration: {duration:.3f}s)")
        
        # Try to parse response log
        if response_body:
            try:
                json_resp = json.loads(response_body)
                truncated_resp = truncate_sensitive_data(json_resp)
                logger.info(f"Response Body: {json.dumps(truncated_resp, ensure_ascii=False)}")
            except Exception:
                 logger.info(f"Response Body (Raw): {len(response_body)} bytes")

        # Reconstruct response execution
        return Response(
            content=response_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )
        
    except Exception as e:
        logger.error(f"Failed to capture response body: {e}")
        # If we failed to read/reconstruct, try to return mostly original response if possible,
        # but here we consumed the iterator.
        # Ideally, we should just fail safe or not consume if it's a streaming file download.
        # For this JSON API, it is safe to assume small payloads.
        return response

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/v2/find-defects", response_model=FindDefectsResponse)
async def find_defects(request: FindDefectsRequest):
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI Service not initialized")
    
    try:
        defects = await ai_service.find_defects(request.screen, request.assertion)
        return FindDefectsResponse(defects=defects)
    except Exception as e:
        logger.exception(f"Error in find_defects: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v2/extract-text", response_model=ExtractTextWithAiResponse)
async def extract_text(request: ExtractTextWithAiRequest):
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI Service not initialized")

    try:
        text = await ai_service.extract_text(request.screen, request.query)
        return ExtractTextWithAiResponse(text=text)
    except Exception as e:
        logger.exception(f"Error in extract_text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8500)
