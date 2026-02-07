# Maestro AI Server

基于 **LangChain v1** 和 **FastAPI** 的 AI 服务，替代 Maestro Cloud 的 AI 功能。

## 功能特性

| API 端点 | 功能 | Maestro 命令 |
|----------|------|--------------|
| `POST /v2/find-defects` | 缺陷检测/断言验证 | `assertWithAI`, `assertNoDefectsWithAI` |
| `POST /v2/extract-text` | 文本提取 | `extractTextWithAI` |

### 可靠性机制

- ✅ **结构化输出**: LangChain v1 `ProviderStrategy` 原生支持
- ✅ **自动重试**: 指数退避重试机制
- ✅ **LangSmith 追踪**: 生产环境调用追踪

## 快速开始

### 1. 配置环境

```bash
cp .env.example .env
# 编辑 .env，填入 Kimi API Key 和 LangSmith API Key
```

### 2. 安装依赖

```bash
uv sync --all-extras
```

### 3. 启动服务

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 配置 Maestro

```bash
export MAESTRO_CLOUD_API_URL=http://localhost:8000
maestro test your_flow.yaml
```

## Docker 部署

```bash
docker compose up -d
```

## 接口说明

### 缺陷检测

```bash
curl -X POST http://localhost:8000/v2/find-defects \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"screen": "BASE64_IMAGE", "assertion": "页面显示登录按钮"}'
```

### 文本提取

```bash
curl -X POST http://localhost:8000/v2/extract-text \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"screen": "BASE64_IMAGE", "query": "提取页面标题"}'
```

## 开发

### 运行测试

```bash
uv run pytest tests/ -v
```

### 项目结构

```
app/
├── main.py           # FastAPI 入口
├── config.py         # 配置管理
├── api/v2/           # API 端点
├── agents/           # LangChain Agent
├── services/         # 业务服务层
├── schemas/          # Pydantic 模型
├── core/             # 核心组件
└── utils/            # 工具函数
```

## 扩展新命令

1. `app/schemas/` - 定义请求/响应模型
2. `app/agents/prompts/` - 编写 Prompt
3. `app/agents/` - 实现 Agent 类
4. `app/services/` - 添加 Service
5. `app/api/v2/` - 注册路由

## 技术栈

- Python 3.11+
- LangChain v1.2.9
- FastAPI
- Kimi (moonshot-v1-vision)
- LangSmith
