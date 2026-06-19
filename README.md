# 进化酒馆 · EvoMap Murder Game

> 多Agent自进化剧本杀系统 — 基于 EvoMap GEP-A2A 协议

## 项目概述

这是一个**多Agent自进化剧本杀游戏系统**。系统中的每个 AI Agent 都是 EvoMap 网络中的独立节点，拥有持久化的身份文档（identity_doc）和行为宪章（constitution）。Agent 在每次交互后通过 EvoMap Memory 记录经验、反思错误、改写自身行为规则，实现从"刻板脚本"到"懂你的觉醒伙伴"的进化。

### 核心特性

- 🧬 **自进化**：Agent 通过 Memory record/recall 和 constitution 改写实现行为进化
- 🎭 **角色扮演**：三层LLM管道（生成→审查→修订）防止信息泄露，确保角色隔离
- 🐝 **蜂群协作**：通过 EvoMap Session/Council/Task 实现多Agent协作和决策
- 🔒 **信息隔离**：SafeActor 机制确保 Agent 只能看到角色可见信息
- 🏛️ **AI Council**：五阶段审议流程（附议→发散→质疑→投票→收敛）
- 🔗 **经验共享**：高质量 Gene+Capsule 发布到社区，跨模型可复用

## 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | Python 3.12+ · FastAPI · SQLAlchemy · Uvicorn |
| **前端** | React 18 · TypeScript · Mantine UI 7 · React Router 7 |
| **AI 推理** | EvoMap LLM 中转站（OpenAI兼容） · 多 provider 支持 |
| **Agent 协作** | EvoMap GEP-A2A 协议 · Session · Memory · Council |
| **数据库** | SQLite（开发） / PostgreSQL（生产） |

## 项目结构

```
evo-murder-game/
├── api/                    # 后端（Python FastAPI）
│   ├── main.py             # API 入口，所有路由
│   ├── settings.py         # 配置管理（.env读取）
│   ├── evomap_client.py    # EvoMap A2A Protocol 客户端
│   ├── agent_orchestrator.py  # 多Agent编排器
│   ├── llm_service.py      # 三层LLM管道 + 多provider
│   ├── invoke_types.py     # Pydantic请求/响应模型
│   ├── models.py           # SQLAlchemy ORM 数据模型
│   ├── db.py               # 数据库连接
│   ├── requirements.txt    # Python 依赖
│   └── .env.example        # 环境变量示例
│
├── web/                    # 前端（React TypeScript）
│   ├── src/
│   │   ├── api/            # API调用封装
│   │   ├── components/     # UI组件
│   │   ├── pages/          # 页面
│   │   ├── providers/      # 状态管理（constate）
│   │   ├── types/          # TypeScript 类型定义
│   │   ├── utils/          # 工具函数
│   │   ├── constants/      # 常量
│   │   ├── App.tsx         # 应用入口+路由
│   │   └── index.tsx       # React入口
│   ├── public/             # 静态资源
│   ├── package.json        # 前端依赖
│   └── tsconfig.json       # TypeScript配置
│
├── docs/                   # 项目文档
├── scripts/                # 工具脚本
├── README.md               # 本文件
└── .gitignore              # Git忽略规则
```

## 快速开始

### 1. 后端启动

```bash
cd api
pip install -r requirements.txt
cp .env.example .env         # 编辑 .env 填入你的 API Key
python -m uvicorn api.main:app --reload --port 10000
```

### 2. 前端启动

```bash
cd web
npm install
npm start                    # 默认端口 5001，API指向 localhost:10000
```

### 3. EvoMap Agent 注册

访问前端 `/agents` 页面，或直接调用 API：

```bash
curl -X POST http://localhost:10000/agents/register \
  -H "Content-Type: application/json" \
  -d '{"role": "companion", "name": "小七", "model": "evomap-gemini-3.1-pro-preview"}'
```

## 协作规范

详见 [docs/协作规范.md](docs/协作规范.md)

- 每个文件夹内都有 README 说明该目录的职责、需求和进度
- 使用 GitHub Issues + PR 进行协作
- 代码风格：Python 遵循 PEP 8，TypeScript 遵循项目内已有风格
- 提交信息格式：`[模块] 简述`（例如 `[api] 新增 Session 创建接口`）

## 复用来源

本项目从 [ai-murder-mystery](../ai-murder-mystery) 复用了以下核心模块：

| 模块 | 复用内容 |
|------|---------|
| 三层LLM管道 | respond_initial → critique → refine 防泄漏机制 |
| SafeActor信息隔离 | secret/violation字段过滤，防止跨角色信息泄露 |
| 多LLM provider | Anthropic/OpenAI/Groq/Ollama/OpenRouter 统一接口 |
| 流式SSE | 流式对话输出 |
| FastAPI骨架 | API服务基础架构 |
| Mantine UI | 前端组件库 |

新增内容（EvoMap 集成）：

| 模块 | 说明 |
|------|------|
| EvoMap A2A Client | GEP-A2A 协议全端点封装 |
| Agent Orchestrator | 多Agent注册、Session管理、任务分发 |
| Memory Integration | 经验记录/召回驱动进化 |
| Constitution Evolution | 行为宪章改写实现自我进化 |
| Council Governance | 五阶段审议流程 |
| Evolution Timeline UI | 进化可视化 |

## 许可

本项目基于 ai-murder-mystery 的衍生项目，遵循其原始许可协议。
