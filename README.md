# 企业级 AI 工单助手

一个面向企业客服 / IT 支持场景的 AI 工单管理项目。项目包含 FastAPI 后端、SQLite 数据库、原生 HTML/CSS/JavaScript 前端，并接入 OpenAI-compatible LLM API 生成工单分析和回复建议。

## 功能

- 创建工单
- 查看工单列表
- 按关键词、优先级、状态搜索工单
- 更新工单状态
- 使用 AI 生成问题分类、建议优先级、处理建议和用户回复话术

## 技术栈

- Backend: Python, FastAPI, Pydantic, SQLite
- Frontend: HTML, CSS, JavaScript, fetch API
- AI: OpenAI-compatible LLM API
- Engineering: Git, GitHub, requirements.txt, environment variables

## 项目结构

```text
enterprise-ai-ticket-agent/
  backend/
    main.py
    requirements.txt
  frontend/
    index.html
    style.css
    app.js
```

## 后端启动

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

启动后访问：

```text
http://127.0.0.1:8000/docs
```

## 前端运行

后端启动后，直接用浏览器打开：

```text
frontend/index.html
```

前端默认请求：

```text
http://127.0.0.1:8000
```

## AI 配置

如果使用 OpenAI-compatible 中转站，请在运行环境中配置：

```text
OPENAI_API_KEY=你的 API Key
OPENAI_BASE_URL=你的中转站接口地址
OPENAI_MODEL=你的模型名
```

如果只测试工单 CRUD 和搜索功能，可以不配置 AI 环境变量。
