# api/db/ · README

## 职责
数据持久化——SQLAlchemy ORM 模型 + 数据库连接管理。
支持 PostgreSQL（生产）和 SQLite（开发）双模式。

## 文件清单
| 文件 | 说明 |
|------|------|
| `models.py` | 所有 ORM 模型（15个表：剧本/角色/推理题/剧透故事/证物定义/Agent节点/游戏会话/对话记录/进化记录/运行时证物/证物反应/证物发现/证物出示/证物组合/游戏进度） |
| `database.py` | 数据库连接引擎 + 初始化 + Session 工具 |
| `__init__.py` | 模块导出 |

## ORM 模型清单

### 剧本与游戏内容层
| 模型 | 表名 | 说明 |
|------|------|------|
| `Script` | scripts | 剧本（标题/故事/难度/时长/封面/设置/角色列表/证物定义/推理题） |
| `Character` | characters | 角色（名字/性格/秘密/违规/角色标记/头像） |
| `QuizQuestion` | quiz_questions | 推理题（题目/选项/正确答案/顺序） |
| `SpoilerStory` | spoiler_stories | 剧透故事（完整真相还原/AI模型/生成信息） |
| `ScriptEvidence` | script_evidences | 剧本级证物定义（创建时预设的证物模板） |

### Agent 与协作层
| 模型 | 表名 | 说明 |
|------|------|------|
| `AgentNode` | agent_nodes | Agent节点（EvoMap node_id/secret/角色/constitution/identity_doc） |
| `GameSession` | game_sessions | 游戏会话（EvoMap session_id/剧本/参与者/进度/结果） |
| `ConversationTurn` | conversation_turns | 对话记录（每轮的原始/批评/修订/最终回复） |
| `EvolutionRecord` | evolution_records | 进化记录（Memory本地副本 + constitution改写历史） |

### 运行时证物系统层
| 模型 | 表名 | 说明 |
|------|------|------|
| `EvidenceRecord` | evidences | 运行时证物（动态状态：state/unlockLevel/关联） |
| `EvidenceReactionRecord` | evidence_reactions | 证物反应（角色对证物的预设反应/basic/contradiction/breakthrough） |
| `EvidenceDiscoveryRecord` | evidence_discoveries | 证物发现记录（谁/何时/以何种方式发现） |
| `EvidencePresentationRecord` | evidence_presentations | 证物出示记录（向角色出示证物及AI反应） |
| `EvidenceCombinationRecord` | evidence_combinations | 证物组合记录（两证物组合尝试和结果） |
| `GameProgressRecord` | game_progress | 游戏进度（已发现/出示/组合证物、游戏阶段、耗时） |

## 当前需求
- [ ] 添加 Alembic 迁移工具（数据库 schema 变更管理）
- [ ] AgentNode.node_secret 的安全存储（加密？只存本地文件？）
- [ ] 索引优化（session_id/script_id 高频查询字段）
- [ ] 数据清理策略（长期会话的历史记录归档）

## 进度
- ✅ 15个核心 ORM 模型完成（6个原有 + 9个新增）
- ✅ PostgreSQL / SQLite 双模式支持
- ✅ 数据库初始化逻辑（create_all，幂等）
- ✅ 剧本→角色/推理题/证物定义的完整级联关系
- ✅ 运行时证物→反应/发现/出示/组合的完整级联关系
- ✅ 数据转换工具函数（ORM ↔ 前端字典格式，含 camelCase 字段映射）
- ✅ 从 ai-murder-mystery 的 models.py 复用基础结构并适配

## 疑问
- SQLite 文件放在 data/murder_mystery.db——这个路径是否合适？
- AgentNode.node_secret 存在数据库中是否有安全风险？应该只存本地文件？
- GameSession 与 EvoMap Session 的映射关系——两者 ID 是否应该关联？
- 证据模型中 related_actors/related_evidences 用 JSON 存关联 vs 建关联表，哪种更优？