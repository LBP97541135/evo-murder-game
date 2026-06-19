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
| `__init__.py` | - | - | 模块导出 |

## 路由依赖关系

```
health.py → orchestrator（读 agents/sessions 数量）
agents.py → AgentOrchestrator, AgentNode, AgentRole, EvoMapClient
invoke.py → llm_service.invoke_with_pipeline, ROLE_SYSTEM_PROMPTS
game.py   → AgentOrchestrator, AgentRole
memory.py → AgentOrchestrator（找Agent → 调用 client.memory_*）
```

## 当前需求
- [ ] 添加剧本 CRUD 路由（/scripts/save, /scripts/list, /scripts/{id}）
- [ ] 添加证据路由（/evidence/create, /evidence/present, /evidence/combine）
- [ ] 添加图像生成路由（/generate_avatar, /generate_cover, /generate_background）
- [ ] 添加流式 SSE 路由（/invoke/stream）
- [ ] 添加 Council 路由（/council/propose, /dialog）
- [ ] 添加资产发布路由（/assets/publish, /assets/search）

## 进度
- ✅ 5个路由文件拆分完成（从 main.py 的单体拆出）
- ✅ 所有现有端点保持功能一致
- ✅ main.py 只做 app 初始化 + 路由挂载

## 疑问
- 路由文件之间的全局状态（orchestrator）是通过 `from api.main import orchestrator` 引入的——这是循环依赖吗？
  → 不是：main.py 先创建 orchestrator，路由文件导入它时 main.py 已经初始化完毕
- 后续路由文件越来越多时，是否需要进一步拆分？（比如 game/ 下分 session.py, broadcast.py, reflect.py）
