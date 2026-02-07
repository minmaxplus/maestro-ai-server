# Maestro AI Server Dockerfile
# 基于 Python 3.11，使用 uv 管理依赖
# @author LJY

FROM python:3.11-slim

# 安装 uv
RUN pip install uv

WORKDIR /app

# 复制依赖文件
COPY pyproject.toml README.md ./

# 安装依赖
RUN uv pip install --system -e .

# 复制应用代码
COPY app/ ./app/

# 创建非 root 用户
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
