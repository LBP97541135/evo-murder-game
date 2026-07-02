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
│   ├── core/               # 核心模块（错误处理、响应格式、日志）
│   ├── models/             # ORM 模型（按领域拆分）
│   ├── schemas/            # Pydantic 请求/响应模型
│   ├── repositories/       # 数据访问层
│   ├── services/           # 业务逻辑层
│   ├── routers/            # HTTP 路由层
│   ├── domain/             # 领域规则和 prompt
│   ├── integrations/       # 第三方集成（EvoMap 等）
│   ├── agents/             # 多Agent编排系统
│   ├── llm/                # LLM 三层管道 + 多Provider
│   ├── db/                 # 数据持久化（ORM/连接）
│   └── tests/              # 单元测试
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

### 1. 后端启动（必须使用端口 8000）

```bash
# 克隆仓库
git clone <repo-url> && cd evo-murder-game

# 创建并激活虚拟环境
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

# 安装依赖
pip install -r api/requirements.txt

# 配置环境变量（复盘、DM评分、Skill 生成均依赖 LLM，必须配置 API_KEY）
cp api/config/.env.example api/config/.env
# 编辑 api/config/.env，填入你的 API_KEY 和 OPENAI_API_BASE

# 启动后端（端口必须为 8000，前端默认请求 localhost:8000）
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

> **Windows PowerShell 无法激活虚拟环境时**：无需修改执行策略，直接用：
> `.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 8000`

验证后端：浏览器访问 <http://localhost:8000/health> 应返回 `ok`。

### 2. 前端启动

```bash
cd web
npm install
npm start    # 默认端口 3000，API 代理到 localhost:8000
```

前端 `package.json` 的 `proxy` 已配置为 `http://localhost:8000`，
`npm start` 无需额外环境变量即可跨平台（Windows/macOS/Linux）运行。

如需自定义后端地址：
```bash
# macOS / Linux
REACT_APP_API_URL=http://your-host:8000 npm start

# Windows PowerShell
$env:REACT_APP_API_URL="http://your-host:8000"; npm start
```

### 3. 数据库

仓库自带 `data/murder_mystery.db`（含 13 个剧本、85 个角色），clone 后即可使用。
若数据库为空或需要导入新剧本，运行：
```bash
python scripts/import_xiutie_script.py
```

### 4. 运行测试

```bash
# 运行所有测试
pytest api/tests/

# 运行特定测试文件
pytest api/tests/test_smoke_core_flow.py
pytest api/tests/test_skill_service.py

# 生成测试覆盖率报告
pytest --cov=api --cov-report=html
```

### 5. 开始游戏

1. 浏览器打开 <http://localhost:3000> → 剧本库
2. 选择剧本 → 选角 → 进入游戏
3. 游戏流程：开场介绍 → 自由调查 → 提交推理 → 真相揭示 → 复盘反思
4. 复盘看板：游戏结束后点击「打开复盘看板」跳转 `/review/:id?session=...`

### 重要注意事项

- **端口必须为 8000**：前端所有 API 请求默认指向 `localhost:8000`，改端口会导致阶段切换、投票、复盘全部失败
- **必须配置 API_KEY**：`api/config/.env` 中的 `API_KEY` 和 `OPENAI_API_BASE` 是复盘评分、胶囊生成的必要条件，缺配则这些功能静默失败
- **`.env` 不在 git 中**：每位协作者需自行从 `.env.example` 复制并填写
- **从项目根目录启动后端**：不要进入 `api/` 目录再启动，项目使用 `api.*` 绝对导入

## 后端 API 总览

后端采用分层架构（routers → services → repositories → models），已实现完整游戏流程。详细接口说明见 [docs/API接口文档.md](docs/API接口文档.md)。

### 游戏引擎阶段流转

```
setup → intro → script_reading → investigation → deduction → voting → reveal → review
 准备    介绍    剧本阅读          调查阶段        推理阶段    投票    揭晓    复盘
```

### API 端点一览（重构后）

| 模块 | 端点 | 方法 | 功能 |
|------|------|------|------|
| **健康检查** | `/health` | GET | 健康检查 |
| **剧本** | `/scripts/` | GET | 剧本列表 |
| | `/scripts/{id}` | GET | 剧本详情 |
| | `/scripts/import` | POST | 导入剧本 |
| **会话** | `/sessions/` | POST | 创建游戏会话 |
| | `/sessions/{id}` | GET | 获取会话详情 |
| | `/sessions/{id}/snapshot` | GET | 获取游戏快照 |
| | `/sessions/{id}/end` | POST | 结束游戏 |
| **选角** | `/sessions/{id}/cast/` | POST | 设置选角 |
| | `/sessions/{id}/cast/` | GET | 获取选角信息 |
| | `/sessions/{id}/cast/` | DELETE | 重置选角 |
| **阶段** | `/sessions/{id}/phase/` | GET | 获取当前阶段 |
| | `/sessions/{id}/phase/advance` | POST | 推进到下一阶段 |
| | `/sessions/{id}/phase/force` | POST | 强制跳转阶段 |
| **对话** | `/sessions/{id}/messages/` | GET | 获取消息列表 |
| | `/sessions/{id}/messages/` | POST | 发送消息 |
| | `/sessions/{id}/messages/threads` | GET | 获取对话线程列表 |
| | `/sessions/{id}/messages/threads` | POST | 创建对话线程 |
| **证物** | `/sessions/{id}/evidences/` | GET | 获取证物列表 |
| | `/sessions/{id}/evidences/public` | GET | 获取公开证物 |
| | `/sessions/{id}/evidences/discover` | POST | 发现证物 |
| | `/sessions/{id}/evidences/present` | POST | 出示证物 |
| **复盘** | `/sessions/{id}/review/` | GET | 获取复盘报告 |
| | `/sessions/{id}/review/run` | POST | 运行复盘 |
| **Skill** | `/skills/` | GET | Skill 列表 |
| | `/skills/` | POST | 创建 Skill |
| | `/skills/{id}` | GET/PATCH/DELETE | Skill CRUD |
| | `/skills/search` | POST | 搜索 Skill |
| | `/skills/import` | POST | 导入 Skill |
| | `/skills/{id}/export` | GET | 导出 Skill |
| | `/skills/{id}/review` | POST | 审核 Skill |
| **Agent** | `/agents/` | GET | Agent 列表 |
| | `/agents/` | POST | 创建 Agent |
| | `/agents/{id}` | GET | Agent 详情 |
| | `/agents/{id}/state` | GET | Agent 运行时状态 |
| **用户** | `/users/profile` | GET/PATCH | 用户信息 |

### 最小可玩流程

```
创建会话 → 选角 → 推进阶段(setup→intro→investigation)
→ 对话/出示证物 → 投票 → 揭示真相 → 复盘
```

### 待完善功能

| 优先级 | 功能 | 说明 | 状态 |
|--------|------|------|------|
| P0 | AI调用集成game_engine | 根据阶段动态调整prompt | ✅ 已完成 |
| P0 | AI调用自动保存对话 | invoke路由里调conversations/save | ✅ 已完成 |
| P1 | 后剧情模式 | 投票后自动触发凶手交代+DM真相揭晓 | ✅ 已完成 |
| P1 | DM提示系统 | 根据进度自动生成分级提示（L1-L4） | ✅ 已完成 |
| P1 | 角色交互增强 | 证物出示无预设反应时由LLM动态生成 | ✅ 已完成 |
| P2 | CrewAI Agent架构 | 替换当前AgentOrchestrator | ❌ 待排期 |
| P2 | Agent自动进化触发 | 局后LLM自动改写constitution | ✅ 已有基础逻辑 |
| P2 | 多玩家支持 | 多人投票、按角色信息隔离 | ❌ 待排期 |

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

---

## 项目重构

本项目已完成架构重构，升级为分层清晰、模块独立、可脱离 EvoMap 独立运行的 AI 剧本杀引擎。

### 重构亮点

- **分层架构**: routers → services → repositories → models，职责清晰
- **Skill 资产系统**: 替代旧 Capsule 系统，支持创建、搜索、注入、导入导出
- **EvoMap 解耦**: 核心游戏流程不依赖 EvoMap，EvoMap 作为可选集成
- **Prompt 文件化**: 所有 prompt 以 markdown 文件管理，不再散落在代码中
- **数据库重构**: 引入 Alembic 迁移，新表结构清晰
- **前端重构**: GamePage 拆分为独立组件和 hooks，以服务端 snapshot 为唯一状态源
- **完善测试**: 核心流程 smoke tests 和 Skill 系统单元测试全覆盖
- **API 文档**: 完整的接口文档，包含请求/响应示例和错误码说明

### 新目录结构

```
api/
  core/          # 核心配置、错误处理、统一响应
  models/        # ORM 模型（按领域拆分）
  schemas/       # Pydantic DTO
  repositories/  # 数据访问层
  services/      # 业务逻辑层
  routers/       # HTTP 路由层
  domain/        # 领域规则和 prompt
  integrations/  # 第三方集成（EvoMap 等）
  tests/         # 单元测试
```

### 测试覆盖

项目包含完善的测试套件：

- **test_smoke_core_flow.py**: 核心流程 smoke tests，覆盖健康检查、会话创建、剧本列表、选角、阶段推进、对话、证物、复盘等
- **test_skill_service.py**: Skill 系统测试，覆盖 CRUD、搜索、注入、导入导出、经验转化等
- **test_session_service.py**: 会话服务测试
- **test_prompt_loader.py**: Prompt 加载器测试

运行测试：

```bash
# 运行所有测试
pytest api/tests/

# 运行特定测试文件
pytest api/tests/test_smoke_core_flow.py
pytest api/tests/test_skill_service.py

# 生成测试覆盖率报告
pytest --cov=api --cov-report=html
```

### 文档

- [API 接口文档](docs/API接口文档.md) - 完整的 RESTful API 接口说明
- [项目重构方案](docs/项目重构方案.md) - 架构重构详细设计
- [核心游戏流程迁移方案](docs/核心游戏流程迁移方案.md) - 从旧版迁移指南
- [协作规范](docs/协作规范.md) - 开发协作规范

### 快速启动

```bash
# 后端
cd api
pip install -r requirements.txt
uvicorn api.main:app --reload

# 前端
cd web
npm install
npm start
```
