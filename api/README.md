# api/ · README

## 职责
后端 API 服务，基于 Python FastAPI。
负责所有后端逻辑：Agent 管理、EvoMap 通信、LLM 推理、游戏 Session、数据持久化、剧本管理、证物系统、剧透故事。

## 本地运行

以下命令均需要在项目根目录执行，即包含 `api/`、`web/` 和 `data/` 的目录。

### 1. 环境要求

- Python 3.10 及以上，推荐 Python 3.11。
- 默认使用 SQLite，无需单独安装数据库。
- 如果需要调用 AI 推理接口，需要准备对应 Provider 的 API Key，或者运行本地 Ollama。

### 2. 创建虚拟环境

Windows PowerShell：

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 禁止执行激活脚本，可以不激活环境，后续直接使用：

```powershell
.\.venv\Scripts\python.exe
```

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

开发环境建议安装可更新的依赖清单：

```powershell
python -m pip install --upgrade pip
python -m pip install -r api/requirements.txt
```

需要严格复现当前开发环境时，使用锁定版本：

```powershell
python -m pip install -r api/requirements-lock.txt
```

未激活 Windows 虚拟环境时：

```powershell
.\.venv\Scripts\python.exe -m pip install -r api/requirements.txt
```

### 4. 配置环境变量

在项目根目录创建 `.env`。`api/config/settings.py` 使用 `load_dotenv()`，
因此从项目根目录启动时读取的是根目录下的 `.env`。

最小配置示例：

```dotenv
# AI Provider：openai / anthropic / groq / openrouter / ollama
INFERENCE_SERVICE=openai
MODEL=evomap-gemini-3.1-pro-preview
API_KEY=替换为实际密钥
OPENAI_API_BASE=https://api.evomap.ai/v1
MAX_TOKENS=8192

# EvoMap；暂时不使用远程节点时可以留空
EVOMAP_HUB_URL=https://evomap.ai
EVOMAP_NODE_ID=
EVOMAP_NODE_SECRET=

# 数据库；DB_CONN_URL 留空时使用 SQLite
DB_CONN_URL=
SQLITE_PATH=data/murder_mystery.db

DEBUG=true
```

只测试健康检查、剧本读取等不触发 LLM 的接口时，`API_KEY` 可以暂时留空。
调用 `/invoke`、流式 AI、Agent 意图生成等接口时必须配置可用的模型服务。

使用本地 Ollama 的示例：

```dotenv
INFERENCE_SERVICE=ollama
MODEL=qwen2.5:7b
OLLAMA_URL=http://localhost:11434
API_KEY=
```

使用 PostgreSQL 时设置：

```dotenv
DB_CONN_URL=postgresql+psycopg://用户名:密码@localhost:5432/数据库名
```

### 5. 启动后端

推荐从项目根目录启动：

```powershell
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 10001
```

未激活 Windows 虚拟环境时：

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload --host 0.0.0.0 --port 10001
```

macOS / Linux 命令相同：

```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 10001
```

不要进入 `api/` 目录后执行 `uvicorn main:app`，项目内部使用 `api.*`
绝对导入，从项目根目录以 `api.main:app` 启动最稳定。

### 6. 验证服务

启动成功后访问：

- 健康检查：<http://localhost:10001/health>
- Swagger API 文档：<http://localhost:10001/docs>
- OpenAPI JSON：<http://localhost:10001/openapi.json>

PowerShell 验证命令：

```powershell
Invoke-RestMethod http://localhost:10001/health
```

或者：

```powershell
curl.exe http://localhost:10001/health
```

### 7. 同时启动前端

另开一个终端：

```powershell
cd web
npm.cmd install
npm.cmd start
```

前端默认连接 `http://localhost:10001`。需要使用其他后端地址时设置：

```powershell
$env:REACT_APP_API_URL="http://localhost:10001"
npm.cmd start
```

### 常见问题

#### `ModuleNotFoundError: No module named 'api'`

确认当前目录是项目根目录，并使用：

```powershell
python -m uvicorn api.main:app --reload --port 10001
```

#### PowerShell 无法运行 `Activate.ps1`

无需修改系统执行策略，可以直接使用虚拟环境中的 Python：

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 10001
```

#### SQLite 报 `unable to open database file`

确认从项目根目录启动，并且根目录下存在 `data/`。默认数据库文件为：

```text
data/murder_mystery.db
```

#### `/game/create-session` 返回 `No agents registered yet`

创建游戏 Session 前，后端编排器中至少需要一个已注册 Agent。可以先通过
Swagger 调用 `POST /agents/register`。如果只开发页面，前端会降级为本地游戏模式。

#### AI 接口返回认证或模型错误

检查 `.env` 中的 `INFERENCE_SERVICE`、`MODEL`、`API_KEY` 和对应 API Base。
修改 `.env` 后需要重启后端进程。

## 目录结构

```
api/
├── main.py                 ← FastAPI 入口，app初始化 + 路由挂载
├── requirements.txt        ← Python 依赖清单
├── __init__.py             ← 包标记
│
├── config/                 ← 配置管理
│   ├── settings.py         ← .env读取，所有配置变量
│   └── README.md
│
├── evomap/                 ← EvoMap A2A Protocol 客户端
│   ├── evomap_client.py    ← 全端点封装（30+方法）
│   ├── __init__.py
│   └── README.md
│
├── agents/                 ← 多Agent编排系统
│   ├── agent_orchestrator.py ← AgentNode + Orchestrator + 角色模板
│   ├── __init__.py
│   └── README.md
│
├── llm/                    ← LLM 推理服务
│   ├── llm_service.py      ← 三层管道 + 5个Provider + 角色Prompt
│   ├── __init__.py
│   └── README.md
│
├── schemas/                ← Pydantic 数据模型
│   ├── invoke_types.py     ← 所有请求/响应模型 + SafeActor
│   ├── __init__.py
│   └── README.md
│
├── db/                     ← 数据持久化
│   ├── models.py           ← SQLAlchemy ORM 模型（15个表 + 转换函数）
│   ├── database.py         ← 连接引擎 + 初始化 + Session
│   ├── __init__.py
│   └── README.md
│
├── routes/                 ← FastAPI 路由定义
│   ├── health.py           ← /health 健康检查
│   ├── agents.py           ← /agents 注册/列表/心跳/进化
│   ├── invoke.py           ← /invoke AI三层管道
│   ├── game.py             ← /game Session/广播/复盘
│   ├── memory.py           ← /memory 记录/召回/状态
│   ├── scripts.py          ← /scripts 剧本CRUD（保存/列表/详情/删除）
│   ├── evidence.py         ← /evidence 证物系统（创建/查询/出示/组合/进度）
│   ├── spoiler_stories.py  ← /spoiler-stories 剧透故事管理
│   ├── __init__.py
│   └── README.md
│
└── README.md               ← 本文件
```

## 当前需求
- [ ] 实际测试所有 EvoMap 端点调用
- [ ] 实际测试三层 LLM 管道
- [ ] 实现流式 SSE 输出
- [ ] 实现 constitution 自动改写逻辑
- [ ] 添加图像生成路由（头像/封面/背景）
- [ ] 添加 Council 治理路由
- [ ] 证据 LLM 反应对接（/evidence/present 接入 llm_service）

## 进度
- ✅ 项目结构从扁平 → 模块化拆分完成
- ✅ 所有 import 路径更新完毕
- ✅ main.py 只做初始化 + 路由挂载
- ✅ routes 从 main.py 单体拆分为 8 个独立文件
- ✅ 数据库从 6 个表扩展到 15 个表（含游戏引擎完整的证物系统/进度表）
- ✅ 剧本 CRUD API（保存/列表/详情/删除，含角色/证物/封面处理）
- ✅ 运行时证物系统（创建/查询/更新/出示/组合/进度追踪，9个端点）
- ✅ 剧透故事管理（CRUD + 批量删除，6个端点）
- ✅ 全部新增端点集成测试通过

## 疑问
- 每个子目录的 README 中已列出各自的具体疑问
- 最关键的阻塞点：EvoMap hello 端点的实际返回格式需要验证
- 证据 /present 的 AI 反应：是在后端内调用 LLM，还是让前端用 /invoke 自己触发？
