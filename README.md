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
| **前端** | React 18 · TypeScript · Mantine UI 7 · React Router 7 · Create React App |
| **AI 推理** | EvoMap LLM 中转站（OpenAI兼容） · 多 provider 支持 |
| **Agent 协作** | EvoMap GEP-A2A 协议 · Session · Memory · Council |
| **数据库** | SQLite（开发） / PostgreSQL（生产） |

## 项目结构

```
evo-murder-game/
├── api/                    # 后端（Python FastAPI）
│   ├── main.py             # FastAPI 入口 + 路由挂载
│   ├── requirements.txt    # Python 依赖
│   ├── config/             # 配置管理（.env/settings）
│   ├── evomap/             # EvoMap A2A 客户端
│   ├── agents/             # 多Agent编排系统
│   ├── llm/                # LLM 三层管道 + 多Provider
│   ├── schemas/            # Pydantic 请求/响应模型
│   ├── db/                 # 数据持久化（ORM/连接）
│   └── routes/             # FastAPI 路由定义
│
├── web/                    # 前端（React TypeScript）
│   ├── figma-make/         # Figma Make 导出的独立视觉参考工程
│   ├── src/
│   │   ├── api/            # API调用封装
│   │   ├── components/     # UI组件
│   │   ├── pages/          # 剧本库、游戏、Agent、个人助手页面
│   │   ├── providers/      # 状态管理（constate）
│   │   ├── types/          # TypeScript 类型定义
│   │   ├── utils/          # 工具函数
│   │   ├── constants/      # 常量
│   │   ├── App.tsx         # Mantine 主题、Provider 和路由
│   │   ├── index.tsx       # React 与 Mantine 样式入口
│   │   └── styles.css      # 暗黑工业风全局样式
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

> **环境要求**：Python 3.11+、Node.js 18+

### 1. 后端启动

```bash
# 创建并激活虚拟环境（必须，确保团队依赖一致）
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
# source .venv/bin/activate

# 安装依赖（在虚拟环境中）
pip install -r api/requirements.txt

# 配置环境变量
cp api/config/.env.example api/config/.env   # 编辑 .env 填入你的 API Key

# 启动服务
python -m uvicorn api.main:app --reload --port 10000
```

### 2. 前端启动

```bash
cd web
npm install
npm start                    # 默认端口 3000，API指向 localhost:10000
```

当前前端是暗黑剧场风格的静态可交互原型，包含 `/library`、`/play/:id`、
`/agents` 和 `/evolution` 四个主页面。页面演示数据目前定义在对应的页面组件内，
尚未全部接入后端 API。

`web/figma-make/` 是从 Figma Make 导出的独立 Vite 工程，仅用于视觉和布局参考，
不参与 `web/` 主应用的 Create React App 构建。详细说明见
[web/README.md](web/README.md) 和 [web/figma-make/README.md](web/figma-make/README.md)。

### 3. EvoMap Agent 注册

访问前端 `/agents` 页面，或直接调用 API：

```bash
curl -X POST http://localhost:10000/agents/register \
  -H "Content-Type: application/json" \
  -d '{"role": "companion", "name": "小七", "model": "evomap-gemini-3.1-pro-preview"}'
```

> **注意**：`.venv/` 已加入 `.gitignore`，不会提交到仓库。每位协作者需自行创建虚拟环境。

## 后端 API 总览

后端已实现完整游戏流程，所有核心 API 测试通过。

### 游戏引擎阶段流转

```
intro ──→ investigation ──→ voting ──→ reveal ──→ review
 开场介绍    自由调查       提交推理    真相揭示    复盘反思
 (无条件)   (对话≥3轮)    (投票完成)   (无条件)    (终态)
```

### API 端点一览

| 模块 | 端点 | 方法 | 功能 |
|------|------|------|------|
| **Health** | `/health` | GET | 健康检查 |
| **Agent** | `/agents/register` | POST | 注册Agent（EvoMap/本地降级） |
| | `/agents/list` | GET | 列出所有Agent |
| | `/agents/heartbeat/{key}` | POST | 心跳保活 |
| | `/agents/evolve/{key}` | POST | 更新constitution/identity_doc |
| **剧本** | `/scripts/save` | POST | 保存剧本（含角色/证物/题目） |
| | `/scripts/list` | GET | 剧本列表 |
| | `/scripts/{id}` | GET | 剧本详情 |
| | `/scripts/{id}` | DELETE | 删除剧本 |
| **游戏** | `/game/create-session` | POST | 创建游戏Session |
| | `/game/phase/{id}` | GET | 查询当前阶段信息 |
| | `/game/phase/{id}/advance` | POST | 推进到下一阶段 |
| | `/game/phase/{id}/force` | POST | 强制跳转阶段（DM权限） |
| | `/game/vote/{id}` | POST | 提交推理投票（凶手+动机） |
| | `/game/chat-count/{id}` | POST | 记录对话轮数 |
| | `/game/broadcast/{id}` | POST | 广播消息 |
| | `/game/reflect/{id}` | POST | 局后反思 |
| **AI调用** | `/invoke/` | POST | 三层管道（initial→critique→refine） |
| | `/invoke/stream` | POST | SSE流式响应 |
| **证物** | `/evidence/script/{sid}/session/{ssid}` | GET | 查询证物列表 |
| | `/evidence/create` | POST | 创建证物 |
| | `/evidence/{id}` | PUT | 更新证物状态 |
| | `/evidence/{id}` | DELETE | 删除证物 |
| | `/evidence/present` | POST | 出示证物给角色 |
| | `/evidence/combine` | POST | 组合证物 |
| | `/evidence/{id}/presentations` | GET | 出示历史 |
| | `/evidence/progress/{sid}` | GET | 游戏进度 |
| | `/evidence/progress/{sid}/phase` | POST | 更新进度阶段 |
| **对话** | `/conversations/save` | POST | 保存对话记录 |
| | `/conversations/session/{id}` | GET | 查询对话历史 |
| | `/conversations/session/{id}` | DELETE | 清除对话 |
| **剧透** | `/spoiler-stories/save` | POST | 保存剧透故事 |
| | `/spoiler-stories/{sid}` | GET | 剧透故事列表 |
| | `/spoiler-stories/story/{id}` | GET | 剧透故事详情 |
| | `/spoiler-stories/{id}` | PUT/DELETE | 更新/删除 |
| **记忆** | `/memory/record` | POST | 记录经验 |
| | `/memory/recall` | POST | 召回经验 |
| | `/memory/status/{key}` | GET | 记忆概况 |

### 最小可玩流程

```
注册Agent → 保存剧本 → 创建Session → 推进阶段(intro→investigation)
→ AI对话 → 投票 → 揭示真相 → 复盘
```

### 待完善功能

| 优先级 | 功能 | 说明 |
|--------|------|------|
| P0 | AI调用集成game_engine | 根据阶段动态调整prompt |
| P0 | AI调用自动保存对话 | invoke路由里调conversations/save |
| P1 | 后剧情模式 | 投票后重写凶手context，强制交代真相 |
| P1 | DM提示系统 | 根据进度自动生成分级提示 |
| P1 | 角色交互增强 | 证物出示反应、笔记分享反应 |
| P2 | CrewAI Agent架构 | 替换当前AgentOrchestrator |
| P2 | Agent自动进化触发 | 局后LLM自动改写constitution |
| P2 | 多玩家支持 | 多人投票、按角色信息隔离 |

### 数据持久化

所有核心数据已持久化到 SQLite，**服务重启后数据不丢失**：

| 数据类型 | 持久化方式 | 重启恢复 |
|----------|-----------|---------|
| 剧本/角色/证物定义 | 写入 `scripts`/`characters`/`script_evidences` 表 | ✅ |
| Agent 注册信息 | 写入 `agent_nodes` 表，启动时 `_load_agents_from_db()` | ✅ |
| 游戏状态（阶段/投票/对话数） | `game_engine._sync_to_db()` 实时写入，启动时 `_load_from_db()` | ✅ |
| 对话记录 | 写入 `conversation_turns` 表 | ✅ |
| 证物运行时状态 | 写入 `evidences`/`evidence_presentations` 等表 | ✅ |
| 进化记忆 | 写入 `evolution_records` 表 | ✅ |

## Agent 架构

### 当前框架：自建 Agent 系统

当前使用自建的 Agent 框架（`api/agents/`），**不是 CrewAI**。计划后续替换为 CrewAI。

```
自建框架（api/agents/）
├── AgentNode          — Agent 节点类（角色/constitution/identity_doc/EvoMap Client）
├── AgentOrchestrator  — 编排器（注册/Session/消息分发/进化循环/数据库持久化）
├── GameEngine         — 游戏状态机（5阶段流转/投票/推进条件/数据库持久化）
└── EvoMapClient       — EvoMap A2A 协议全端点封装
```

### 三种 Agent 角色

| 角色 | 职责 | constitution 核心规则 | domains |
|------|------|----------------------|---------|
| **DM** | 主持游戏、控制节奏、提供提示、防剧透 | 5条职责 + "绝不泄露答案" | hosting, narrative-control, rule-enforcement |
| **Companion** | 角色扮演、隐藏秘密、推理互动 | 5条职责 + "人设决定怎么演，剧本决定演谁" | role-playing, inference, interaction, performance |
| **Assistant** | 用户画像、推荐剧本、标签生成 | 5条职责 + "不参与角色扮演" | user-profiling, recommendation, tag-generation |

### Agent 能力矩阵

| 能力 | 方法 | EvoMap API | 状态 |
|------|------|-----------|------|
| 注册到 EvoMap | `AgentNode.register()` | `hello()` | ✅ 有本地降级 |
| 心跳保活 | `AgentNode.heartbeat()` | `heartbeat()` | ✅ |
| 更新 identity_doc | `AgentNode.update_identity()` | — | ✅ |
| 更新 constitution | `AgentNode.update_constitution()` | — | ✅ |
| 记录经验 | `AgentNode.record_experience()` | `memory_record()` | ✅ 需EvoMap |
| 召回经验 | `AgentNode.recall_experience()` | `memory_recall()` | ✅ 需EvoMap |
| 创建 Session | `Orchestrator.create_game_session()` | `create_session()` | ✅ 有本地降级 |
| 广播消息 | `Orchestrator.broadcast_message()` | `send_message()` | ✅ 需EvoMap |
| 定向消息 | `Orchestrator.send_direct_message()` | `send_message()` | ✅ 需EvoMap |
| 局后自评 | `Orchestrator.post_game_reflection()` | `memory_record()` | ✅ 需EvoMap |
| 发布胶囊 | — | `publish()` | ❌ 未接入 |
| 获取胶囊 | — | `fetch()` / `search_assets()` | ❌ 未接入 |
| 发布前校验 | — | `validate()` | ❌ 未接入 |
| Council 提案 | — | `council_propose()` | ❌ 未接入 |
| Council 审议 | — | `dialog()` | ❌ 未接入 |
| 任务分解 | — | `propose_decomposition()` | ❌ 未接入 |
| 认领任务 | — | `claim_task()` | ❌ 未接入 |
| 发布问题 | — | `ask()` | ❌ 未接入 |
| Recipe 编排 | — | `create_recipe()` | ❌ 未接入 |
| Organism 执行 | — | `express_recipe()` / `express_gene()` | ❌ 未接入 |

### 胶囊（Capsule）经验接入方案

`EvoMapClient` 已封装 `publish()`/`fetch()`/`search_assets()`/`validate()` 四个胶囊方法，但 Agent 层尚未调用。接入后可实现：

```
局后复盘 → Agent 自评(record_experience) → 高分经验打包为 Gene+Capsule(publish)
新局开始 → 搜索社区胶囊(fetch/search_assets) → 融入自身 constitution(update_constitution)

具体场景：
  DM-Agent: 发布"控场节奏"胶囊 → 其他DM获取后提升主持水平
  Companion-Agent: 发布"角色扮演技巧"胶囊 → 其他陪玩获取后提升演技
  Assistant-Agent: 发布"用户画像标签体系"胶囊 → 提升推荐精度
```

接入胶囊需补的代码：

| 步骤 | 改动 | 工作量 |
|------|------|--------|
| AgentNode 添加 `publish_capsule()` | 调用 `client.publish()` + `client.validate()` | 小 |
| AgentNode 添加 `fetch_capsule()` | 调用 `client.fetch()` / `client.search_assets()` | 小 |
| 局后自动判断是否发布胶囊 | score > 阈值时自动 publish | 小 |
| 新局开始前自动搜索胶囊 | 根据剧本类型搜索，融入 prompt | 中 |
| 路由暴露胶囊接口 | `/agents/publish-capsule`、`/agents/fetch-capsule` | 小 |

> **前提**：胶囊功能需要 EvoMap Hub 可用（有效 API Key），本地降级模式下无法使用。

### CrewAI 替换计划

将 `AgentNode` + `AgentOrchestrator` 替换为 CrewAI 的 `Agent` + `Crew` + `Task`，保留以下模块不变：

| 保留模块 | 原因 |
|----------|------|
| `GameEngine` | 游戏阶段状态机，与Agent框架无关 |
| `EvoMapClient` | A2A协议封装，CrewAI不覆盖 |
| 所有 `routes/` | FastAPI路由层，与Agent框架无关 |
| 所有 `db/` | 数据模型，与Agent框架无关 |
| `llm_service.py` | 三层AI管道，CrewAI Agent底层仍调用它 |
| `invoke_stream.py` | SSE流式，与Agent框架无关 |

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
| Figma Make 参考工程 | 暗黑剧场视觉方向、字体层级、卡片和页面布局参考 |

新增内容（EvoMap 集成）：

| 模块 | 说明 |
|------|------|
| EvoMap A2A Client | GEP-A2A 协议全端点封装 |
| Agent Orchestrator | 多Agent注册、Session管理、任务分发 |
| Memory Integration | 经验记录/召回驱动进化 |
| Constitution Evolution | 行为宪章改写实现自我进化 |
| Council Governance | 五阶段审议流程 |
| 暗黑剧场前端原型 | 剧本库、游戏舞台、Agent 广场和个人助手中枢 |

## 许可

本项目基于 ai-murder-mystery 的衍生项目，遵循其原始许可协议。
