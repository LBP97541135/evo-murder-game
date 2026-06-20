# api/routes/ · README

## 职责
FastAPI 路由定义——每个文件对应一组 API 端点，从 main.py 拆分出来。
所有路由通过 main.py 的 `app.include_router()` 挂载。

## 文件清单
| 文件 | 路由前缀 | 端点数 | 说明 |
|------|---------|--------|------|
| `health.py` | `/health` | 1 | 健康检查 |
| `agents.py` | `/agents` | 9 | 注册/列表/心跳/进化/角色系统 |
| `invoke.py` | `/invoke` | 1 | AI三层管道调用 |
| `invoke_stream.py` | `/invoke` | 1 | 流式 SSE 调用 |
| `game.py` | `/game` | 11 | Session/阶段/投票/广播/Agent状态/意图 |
| `memory.py` | `/memory` | 3 | 记录经验/召回经验/状态查询 |
| `scripts.py` | `/scripts` | 2 | 剧本列表/详情（只读） |
| `evidence.py` | `/evidence` | 9 | 证物系统（创建/查询/出示/组合/进度） |
| `spoiler_stories.py` | `/spoiler-stories` | 6 | 剧透故事（保存/列表/详情/更新/删除/批量） |
| `conversations.py` | `/conversations` | 3 | 对话历史（保存/查询/删除） |
| `capsules.py` | `/capsules` | 10 | 胶囊系统（Gene/Capsule/搜索/消费/生成） |

## 路由依赖关系

```
health.py            → orchestrator（读 agents/sessions 数量）
agents.py            → AgentOrchestrator, AgentNode, AgentRole, EvoMapClient
invoke.py            → llm_service.invoke_with_pipeline, ROLE_SYSTEM_PROMPTS
invoke_stream.py     → llm_service（流式调用）
game.py              → AgentOrchestrator, AgentRole, game_engine
memory.py            → AgentOrchestrator（找Agent → 调用 client.memory_*）
scripts.py           → api.db.models（Script/Character/QuizQuestion/ScriptEvidence + 转换函数）
evidence.py          → api.db.models（运行时证物5表 + GameProgress + 转换函数）
spoiler_stories.py   → api.db.models（SpoilerStory + 转换函数）
conversations.py     → api.db.models（对话历史）
capsules.py          → api.evomap.asset_service（胶囊/基因服务）
```

## 完整 API 端点总览

| 方法 | 路径 | 说明 |
|------|------|------|
| **健康检查** |
| GET | `/health` | 服务状态 |
| **Agent 管理** |
| POST | `/agents/register` | 注册 Agent |
| GET | `/agents/list` | Agent 列表 |
| POST | `/agents/heartbeat/{key}` | 心跳保活 |
| POST | `/agents/evolve/{key}` | 进化更新 |
| POST | `/agents/personas/init` | 初始化预设角色 |
| GET | `/agents/personas` | 获取预设角色列表 |
| GET | `/agents/personas/{key}` | 获取角色详情 |
| POST | `/agents/personas/load` | 加载角色到 Agent |
| POST | `/agents/personas/auto-match` | 自动匹配角色 |
| **AI 调用** |
| POST | `/invoke/` | 三层管道调用 |
| POST | `/invoke/stream` | 流式 SSE 调用 |
| **游戏 Session** |
| POST | `/game/create-session` | 创建游戏会话 |
| GET | `/game/phase/{id}` | 获取游戏阶段 |
| POST | `/game/phase/{id}/advance` | 推进阶段 |
| POST | `/game/phase/{id}/force` | 强制跳转阶段 |
| POST | `/game/vote/{id}` | 提交投票 |
| POST | `/game/broadcast/{id}` | 广播消息 |
| POST | `/game/chat-count/{id}` | 记录对话 |
| POST | `/game/reflect/{id}` | 局后反思 |
| GET | `/game/agent-state/{sid}/{key}` | 获取 Agent 游戏状态 |
| GET | `/game/intents/{sid}/{key}` | 获取 Agent 意图 |
| POST | `/game/intents/{sid}/{key}/generate` | 生成 Agent 意图 |
| POST | `/game/intents/{sid}/{key}/approve` | 批准/拒绝意图 |
| POST | `/game/agent-chat/{id}` | Agent 发言 |
| **记忆系统** |
| POST | `/memory/record` | 记录经验 |
| POST | `/memory/recall` | 召回经验 |
| GET | `/memory/status/{key}` | 记忆状态 |
| **剧本查询** |
| GET | `/scripts/list` | 剧本列表 |
| GET | `/scripts/{id}` | 剧本详情 |
| **证物系统** |
| GET | `/evidence/script/{sid}/session/{ses}` | 获取会话证物（支持过滤） |
| POST | `/evidence/create` | 创建运行时证物 |
| PUT | `/evidence/{id}` | 更新证物状态/描述 |
| POST | `/evidence/present` | 向角色出示证物 |
| POST | `/evidence/combine` | 组合证物 |
| GET | `/evidence/{id}/presentations` | 出示历史 |
| GET | `/evidence/progress/{session_id}` | 游戏进度 |
| POST | `/evidence/progress/{session_id}/phase` | 更新游戏阶段 |
| DELETE | `/evidence/{id}` | 删除证物 |
| **对话历史** |
| POST | `/conversations/save` | 保存对话 |
| GET | `/conversations/session/{id}` | 获取会话对话 |
| DELETE | `/conversations/session/{id}` | 删除会话对话 |
| **剧透故事** |
| POST | `/spoiler-stories/save` | 保存剧透故事 |
| GET | `/spoiler-stories/{script_id}` | 剧本的剧透故事列表 |
| GET | `/spoiler-stories/story/{id}` | 剧透故事详情 |
| PUT | `/spoiler-stories/{id}` | 更新剧透故事 |
| DELETE | `/spoiler-stories/{id}` | 删除剧透故事 |
| POST | `/spoiler-stories/batch-delete` | 批量删除 |
| **胶囊系统** |
| POST | `/capsules/genes` | 创建 Gene |
| GET | `/capsules/genes/{id}` | 获取 Gene 详情 |
| GET | `/capsules/genes` | 搜索 Genes |
| POST | `/capsules/genes/{id}/review` | 评审 Gene |
| POST | `/capsules/genes/{id}/generate-capsule` | 从 Gene 生成 Capsule |
| POST | `/capsules/search` | 搜索胶囊 |
| GET | `/capsules/capsules/{id}` | 获取胶囊详情 |
| GET | `/capsules/capsules` | 胶囊列表 |
| DELETE | `/capsules/capsules/{id}` | 删除胶囊 |
| POST | `/capsules/consume` | 消费胶囊 |
| POST | `/capsules/review-and-generate` | 评审并生成胶囊 |

## 当前改动记录（2026-06-20）
- ✅ `scripts.py` 简化为只读版本（移除保存/删除接口，只保留列表/详情）
- ✅ 新增 `capsules.py`（10个端点）和 `conversations.py`（3个端点）
- ✅ `game.py` 扩展到11个端点（新增阶段管理、意图系统、Agent状态）
- ✅ `agents.py` 扩展到9个端点（新增角色系统）
- ✅ 总计59个 API 端点

## 进度
- ✅ 11个路由文件
- ✅ 共59个 API 端点
- ✅ 剧本查询（列表/详情，只读）
- ✅ 运行时证物系统
- ✅ 剧透故事管理
- ✅ Agent 角色系统
- ✅ 游戏阶段管理
- ✅ Agent 意图系统
- ✅ 胶囊系统（Gene/Capsule）
- ✅ 对话历史管理
- ✅ main.py 只做 app 初始化 + 路由挂载

## 疑问
- 路由文件之间的全局状态（orchestrator）是通过 `from api.main import orchestrator` 引入的——这是循环依赖吗？
  → 不是：main.py 先创建 orchestrator，路由文件导入它时 main.py 已经初始化完毕
- 后续路由文件越来越多时，是否需要进一步拆分？（比如 game/ 下分 session.py, broadcast.py, reflect.py）
- 证据 LLM 反应是集成到 `/evidence/present` 端点内，还是由前端单独调用 `/invoke`？