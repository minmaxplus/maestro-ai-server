# Maestro AI Server

这是用于替代 Maestro Cloud 的自定义 AI 服务，支持兼容 OpenAI 接口的大模型（如智谱 GLM-4V）。

## 快速开始

1.  **配置环境**
    修改 `.env` 文件，填入您的 Moonshot API Key。
    ```bash
    OPENAI_API_KEY=your_moonshot_api_key
    OPENAI_API_BASE=https://api.moonshot.cn/v1
    AI_MODEL_NAME=kimi-k2.5
    ```

2.  **启动服务**
    确保已安装 `uv`。
    ```bash
    uv run uvicorn app.main:app --host 0.0.0.0 --port 8500 --reload
    ```

3.  **配置 Maestro 客户端**
    在运行 Maestro 命令时，设置 `MAESTRO_CLOUD_API_URL` 环境变量指向本项目地址。
    ```bash
    export MAESTRO_CLOUD_API_URL=http://localhost:8500
    maestro test your_flow.yaml
    ```

## 接口说明
*   `POST /v2/find-defects`: 视觉断言
*   `POST /v2/extract-text`: 文本提取

## 开发指南

### 运行测试
本项目使用 `pytest` 进行单元测试和集成测试。

```bash
# 运行所有测试
uv run python -m pytest

# 运行特定测试文件
uv run python -m pytest tests/test_integration_llm.py
```
