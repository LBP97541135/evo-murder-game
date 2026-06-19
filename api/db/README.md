# api/db/ · README

## 职责
数据持久化——SQLAlchemy ORM 模型 + 数据库连接管理 + 数据转换工具函数。
支持 PostgreSQL（生产）和 SQLite（开发）双模式。

## 文件清单
| 文件 | 说明 |
|------|------|
| `models.py` | 所有 ORM 模型 + 数据转换函数（script_to_dict / evidence_record_to_dict 等） + get_db 依赖注入 |
| `database.py` | 数据库连接引擎 + 初始化 + Session 工具 |
| `__init__.py` | 模块导出 |

## ORM 模型清单

| 模型 | 表名 | 说明 | 来源 |
|------|------|------|------|
| `Script` | scripts | 剧本（含封面文件字段） | 扩展（新增 cover_image_filename/image_path） |
| `Character` | characters | 角色（含头像文件字段） | 扩展（新增 image_filename/image_path） |
| `QuizQuestion` | quiz_questions | 推理验证题目 | **新增**（从 ai-murder-mystery 迁移） |
| `ScriptEvidence` | script_evidences | 剧本静态证物定义 | **新增**（从 ai-murder-mystery 迁移） |
| `SpoilerStory` | spoiler_stories | AI生成剧透故事 | **新增**（从 ai-murder-mystery 迁移） |
| `EvidenceRecord` | evidences | 游戏运行时证物 | **新增**（从 ai-murder-mystery 迁移） |
| `EvidenceReactionRecord` | evidence_reactions | 角色对证物的反应 | **新增**（从 ai-murder-mystery 迁移） |
| `EvidenceDiscoveryRecord` | evidence_discoveries | 证物发现历史 | **新增**（从 ai-murder-mystery 迁移） |
| `EvidencePresentationRecord` | evidence_presentations | 证物出示记录 | **新增**（从 ai-murder-mystery 迁移） |
| `EvidenceCombinationRecord` | evidence_combinations | 证物组合记录 | **新增**（从 ai-murder-mystery 迁移） |
| `GameProgressRecord` | game_progress | 游戏进度 | **新增**（从 ai-murder-mystery 迁移） |
| `AgentNode` | agent_nodes | Agent节点 | 已有（EvoMap） |
| `GameSession` | game_sessions | 游戏会话 | 已有（EvoMap） |
| `ConversationTurn` | conversation_turns | 对话记录 | 已有 |
| `EvolutionRecord` | evolution_records | 进化记录 | 已有（EvoMap） |

## 数据转换函数清单

| 函数 | 说明 |
|------|------|
| `script_to_dict(script)` | Script → 前端 camelCase 字典（含characters/evidences/quiz） |
| `dict_to_script(data, script)` | 前端字典 → Script（更新或新建） |
| `character_to_dict(character)` | Character → 前端字典 |
| `dict_to_character(data, script_id)` | 前端字典 → Character |
| `script_evidence_to_dict(evidence)` | ScriptEvidence → 前端字典 |
| `dict_to_script_evidence(data, script_id)` | 前端字典 → ScriptEvidence |
| `quiz_question_to_dict(question)` | QuizQuestion → 前端字典 |
| `evidence_record_to_dict(evidence)` | 游戏运行时 EvidenceRecord → 前端字典（含reactions） |
| `presentation_record_to_dict(presentation)` | EvidencePresentationRecord → 前端字典 |
| `get_db()` | FastAPI Depends 注入用的 Session yield |

## 当前需求
- [ ] 测试 init_db() 能否正确创建所有新表
- [ ] 验证证据相关的 ORM 关系（cascade delete-orphan）是否正确
- [ ] 测试数据转换函数的前端 camelCase ↔ 后端 snake_case 映射

## 进度
- ✅ 新增 7 个证据相关 ORM 模型（从 ai-murder-mystery 完整迁移）
- ✅ 新增 ScriptEvidence / QuizQuestion / SpoilerStory 模型
- ✅ Script/Character 扩展封面/头像文件字段
- ✅ 完整数据转换函数体系（11个函数）
- ✅ get_db() FastAPI Depends 注入

## 疑问
- Script 的 cover_image 字段（Text）vs cover_image_filename（String）——是否需要统一？
- EvidenceRecord 的 reactions relationship 在 SQLite 下是否正常工作？
