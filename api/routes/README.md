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
| `scripts.py` | `/db` | 9 | 剧本CRUD + 证物管理 + 剧透故事 |
| `evidence.py` | `/evidence` | 7 | 证据运行时CRUD + 出示 + 组合 + 统计 |
| `__init__.py` | - | - | 模块导出 |

## 路由前缀映射

```
/health          → health.py
/agents          → agents.py
/invoke          → invoke.py
/game            → game.py
/memory          → memory.py
/db              → scripts.py     ← 剧本CRUD（save/list/get/delete）+ 证物 + 剧透
/evidence        → evidence.py    ← 游戏运行时证据交互（核心游戏流程）
```

## scripts.py 端点详情（新增）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/db/scripts/save` | POST | 保存剧本（含角色/题目/证物/封面） |
| `/db/scripts/list` | GET | 列出所有剧本 |
| `/db/scripts/{id}` | GET | 获取指定剧本 |
| `/db/scripts/{id}` | DELETE | 删除剧本（含封面文件） |
| `/db/migrate` | POST | 数据迁移占位 |
| `/db/evidences/save` | POST | 保存剧本证物 |
| `/db/evidences/{scriptId}/{evidenceId}` | DELETE | 删除剧本证物 |
| `/db/evidences/{scriptId}` | GET | 获取剧本所有证物 |
| `/db/spoiler-stories/save` | POST | 保存剧透故事 |
| `/db/spoiler-stories/{scriptId}` | GET | 获取剧本所有剧透故事 |

## evidence.py 端点详情（新增，核心游戏流程）

| 端点 | 方法 | 说明 | 核心交互 |
|------|------|------|---------|
| `/evidence/script/{scriptId}/session/{sessionId}` | GET | 获取游戏证物列表 | ✅ 游戏加载时调用 |
| `/evidence/create` | POST | 创建新证物 | ✅ 初始化证据 |
| `/evidence/{id}` | PUT | 更新证物信息（解锁/状态变更） | ✅ 证据发现升级 |
| `/evidence/{id}` | DELETE | 删除证物 | |
| `/evidence/present` | POST | **向角色出示证物 + AI反应** | ⭐ 最核心的游戏交互 |
| `/evidence/{id}/presentations` | GET | 获取证物出示历史 | |
| `/evidence/combine` | POST | **组合两个证物** | ⭐ 证据组合发现新线索 |

## 路由依赖关系

```
health.py   → orchestrator
agents.py   → AgentOrchestrator, AgentNode, AgentRole, EvoMapClient
invoke.py   → llm_service.invoke_with_pipeline, ROLE_SYSTEM_PROMPTS
game.py     → AgentOrchestrator, AgentRole
memory.py   → AgentOrchestrator（找Agent → client.memory_*）
scripts.py  → db.models（Script/Character/QuizQuestion/ScriptEvidence/SpoilerStory + get_db + 转换函数）
evidence.py → db.models（EvidenceRecord全套 + get_db + 转换函数） + llm.evidence_llm_service（AI出示反应）
```

## 当前需求
- [ ] 测试 /db/scripts/save 能否正确保存剧本（含角色和证物）
- [ ] 测试 /evidence/present 能否正确调用AI并返回反应
- [ ] 测试 /evidence/combine 组合逻辑
- [ ] 添加流式 SSE 路由（/invoke/stream）
- [ ] 添加 Council 路由
- [ ] 添加资产发布路由

## 进度
- ✅ 7个路由文件（2个新增：scripts.py + evidence.py）
- ✅ 剧本CRUD完整（从 ai-murder-mystery database_api.py 迁移）
- ✅ 剧透故事CRUD完整（从 ai-murder-mystery spoiler_story_api.py 迁移）
- ✅ 证据运行时CRUD完整（从 ai-murder-mystery evidence_api.py 迁移）
- ✅ 证据出示 + AI反应（核心游戏交互，从 evidence_llm_service 迁移）
- ✅ 证据组合逻辑

## 疑问
- /db 和 /evidence 两个前缀是否太分散？ai-murder-mystery统一用 /db 前缀
- evidence_llm_service.py 位于 api/llm/ 下——其他同学需要在此对接三层管道
