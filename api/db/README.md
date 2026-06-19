# api/db/ · README

## 职责
数据持久化——SQLAlchemy ORM 模型 + 数据库连接管理。
支持 PostgreSQL（生产）和 SQLite（开发）双模式。

## 文件清单
| 文件 | 说明 |
|------|------|
| `models.py` | 所有 ORM 模型（Script/Character/AgentNode/GameSession/ConversationTurn/EvolutionRecord） |
| `database.py` | 数据库连接引擎 + 初始化 + Session 工具 |
| `__init__.py` | 模块导出 |

## ORM 模型清单

| 模型 | 表名 | 说明 |
|------|------|------|
| `Script` | scripts | 剧本（标题/故事/难度/时长/封面/角色列表） |
| `Character` | characters | 角色（名字/性格/秘密/违规/角色标记/头像） |
| `AgentNode` | agent_nodes | Agent节点（EvoMap node_id/secret/角色/constitution/identity_doc） |
| `GameSession` | game_sessions | 游戏会话（EvoMap session_id/剧本/参与者/进度/结果） |
| `ConversationTurn` | conversation_turns | 对话记录（每轮的原始/批评/修订/最终回复） |
| `EvolutionRecord` | evolution_records | 进化记录（Memory本地副本 + constitution改写历史） |

## 当前需求
- [ ] 添加剧本 CRUD API 路由（当前只有模型定义，没有 API）
- [ ] 添加证据模型（ScriptEvidence/EvidenceRecord，从 ai-murder-mystery 复用）
- [ ] 添加剧透故事模型（SpoilerStory）
- [ ] 添加 Alembic 迁移工具（数据库 schema 变更管理）
- [ ] AgentNode.node_secret 的安全存储（加密？只存本地文件？）

## 进度
- ✅ 6个核心 ORM 模型完成
- ✅ PostgreSQL / SQLite 双模式支持
- ✅ 数据库初始化逻辑（create_all）
- ✅ 从 ai-murder-mystery 的 models.py 复用基础结构

## 疑问
- SQLite 文件放在 data/murder_mystery.db——这个路径是否合适？
- AgentNode.node_secret 存在数据库中是否有安全风险？应该只存本地文件？
- GameSession 与 EvoMap Session 的映射关系——两者 ID 是否应该关联？
