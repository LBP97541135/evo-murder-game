# api/ · README

## 职责
后端 API 服务，基于 Python FastAPI。负责：
- Agent 注册与生命周期管理（EvoMap hello/heartbeat）
- 多Agent编排（Agent Orchestrator：DM/陪玩/助手）
- 三层LLM管道（respond_initial → critique → refine）
- 游戏Session创建与消息传递
- Memory 记录与经验召回
- constitution/identity_doc 改写（Agent进化）
- 数据持久化（SQLAlchemy ORM）

## 当前需求
- [ ] 实际测试 evomap_client.py 所有端点调用
- [ ] 完善三层LLM管道的 critique prompt（适配剧本杀场景）
- [ ] 实现流式 SSE 输出（/invoke/stream）
- [ ] 对接剧本数据（从文件/数据库加载）
- [ ] 完善 Agent 注册流程（实际 EvoMap hello 调用）

## 进度
- ✅ settings.py 配置管理（.env读取、多provider URL）
- ✅ evomap_client.py A2A协议全端点封装（hello/session/memory/publish/council/task）
- ✅ agent_orchestrator.py 多Agent编排（注册/Session/自评/进化）
- ✅ llm_service.py 三层管道 + 多provider支持
- ✅ invoke_types.py Pydantic请求/响应模型
- ✅ models.py SQLAlchemy数据模型（Script/Character/AgentNode/GameSession/EvolutionRecord）
- ✅ main.py FastAPI入口 + 全部路由
- ✅ db.py 数据库连接
- 🔲 流式SSE实现
- 🔲 剧本CRUD API
- 🔲 图像生成API（复用火山引擎）

## 疑问
- EvoMap hello 端点的实际返回格式需要验证（文档和实际可能不一致）
- curl 在 Windows 上访问 evomap.ai 有 SSL 问题，需使用 Python requests/httpx
- 三层管道的 critique prompt 需要针对剧本杀场景定制（防剧透 vs 防bug）
