# api/routes/ · README

## 职责
FastAPI 路由定义——每个文件对应一组 API 端点，从 main.py 拆分出来。
所有路由通过 main.py 的 `app.include_router()` 挂载。

## 文件清单
| 文件 | 路由前缀 | 端点数 | 说明 |
|------|---------|--------|------|
| `health.py` | `/health` | 1 | 健康检查 |
| `agents.py` | `/agents` | 4 | 注册/列表/心跳/进化 |
| `invoke.py` | `/invoke` | 1 | AI三层管道调用 |
| `game.py` | `/game` | 3 | 创建Session/广播/复盘 |
| `memory.py` | `/memory` | 3 | 记录经验/召回经验/状态查询 |
| `scripts.py` | `/scripts` | 2 | 剧本列表/详情 |
| `evidence.py` | `/evidence` | 9 | 证物系统（创建/查询/出示/组合/进度） |
| `spoiler_stories.py` | `/spoiler-stories` | 6 | 剧透故事（保存/列表/详情/更新/删除/批量） |

## 路由依赖关系

```
health.py        → orchestrator（读 agents/sessions 数量）
agents.py        → AgentOrchestrator, AgentNode, AgentRole, EvoMapClient
invoke.py        → llm_service.invoke_with_pipeline, ROLE_SYSTEM_PROMPTS
game.py          → AgentOrchestrator, AgentRole
memory.py        → AgentOrchestrator（找Agent → 调用 client.memory_*）
scripts.py       → api.db.models（Script/Character/QuizQuestion/ScriptEvidence + 转换函数）
evidence.py      → api.db.models（运行时证物5表 + GameProgress + 转换函数）
spoiler_stories.py → api.db.models（SpoilerStory + 转换函数）
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
| **AI 调用** |
| POST | `/invoke/` | 三层管道调用 |
| **游戏 Session** |
| POST | `/game/create-session` | 创建游戏会话 |
| POST | `/game/broadcast/{id}` | 广播消息 |
| POST | `/game/reflect/{id}` | 局后反思 |
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
| **剧透故事** |
| POST | `/spoiler-stories/save` | 保存剧透故事 |
| GET | `/spoiler-stories/{script_id}` | 剧本的剧透故事列表 |
| GET | `/spoiler-stories/story/{id}` | 剧透故事详情 |
| PUT | `/spoiler-stories/{id}` | 更新剧透故事 |
| DELETE | `/spoiler-stories/{id}` | 删除剧透故事 |
| POST | `/spoiler-stories/batch-delete` | 批量删除 |

## 当前需求
- [ ] 添加图像生成路由（/generate_avatar, /generate_cover, /generate_background）
- [ ] 添加流式 SSE 路由（/invoke/stream）
- [ ] 添加 Council 路由（/council/propose, /dialog）
- [ ] 添加资产发布路由（/assets/publish, /assets/search）
- [ ] 证据 /present 端点的 AI 反应对接 LLM（当前为预设模板文字）

## 进度
- ✅ 8个路由文件拆分完成（从 main.py 的单体拆出）
- ✅ 共26个 API 端点（原有11个 + 新增17个 - 移除2个）
- ✅ 所有现有端点保持功能一致
- ✅ 剧本查询（列表/详情）
- ✅ 运行时证物系统（创建/查询/出示/组合/进度追踪）
- ✅ 剧透故事管理（含批量删除）
- ✅ 集成测试 13/13 通过
- ✅ main.py 只做 app 初始化 + 路由挂载

## 疑问
- 路由文件之间的全局状态（orchestrator）是通过 `from api.main import orchestrator` 引入的——这是循环依赖吗？
  → 不是：main.py 先创建 orchestrator，路由文件导入它时 main.py 已经初始化完毕
- 后续路由文件越来越多时，是否需要进一步拆分？（比如 game/ 下分 session.py, broadcast.py, reflect.py）
- 证据 LLM 反应是集成到 `/evidence/present` 端点内，还是由前端单独调用 `/invoke`？