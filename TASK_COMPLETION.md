# 任务完成总结

## 任务 1：数据迁移脚本 ✓

### 创建的文件

1. **scripts/migrate_legacy_data.py**
   - 实现从旧表到新表的数据迁移
   - 支持 10 个表的迁移映射
   - 自动备份数据库
   - 幂等执行（检查目标表是否已有数据）
   - 打印迁移统计信息
   - 使用方法：`python scripts/migrate_legacy_data.py`

2. **scripts/validate_migration.py**
   - 对比旧表和新表的数据量
   - 检查关键字段映射是否正确
   - 输出校验报告
   - 使用方法：`python scripts/validate_migration.py`

### 迁移映射关系

1. `scripts` → `scripts`（补充新字段 status, metadata_json, duration_minutes）
2. `characters` → `script_characters`（context→public_context, secret→private_secret, violation→behavior_rules, image→avatar_image）
3. `spoiler_stories` → `script_truths`（content→global_story, 第一条 content→truth_summary）
4. `game_sessions` → `game_sessions` + `game_phase_events`（result JSON 拆分到 metadata_json, phase_history 拆分为事件）
5. `conversation_turns` → `conversation_threads` + `conversation_messages`（每个 session 创建 public thread，每轮对话创建 message）
6. `evidences` → `evidence_instances`（字段基本对应，增加 is_public 字段）
7. `agent_nodes` → `agents`（node_id→external_ref, 新增 external_provider="evomap"）
8. `agent_game_states` → `agent_runtime_states`（agent_key→agent_id, chat_history_json→short_memory, key_facts_json→key_facts, discovered_evidences_json→known_evidence_ids, loaded_capsule_ids_json→loaded_skill_ids, intents_json→intent_json）
9. `genes` → `experience_records`（score→self_score）
10. `capsules` → `skills`（title→name, content→prompt_content, gene_id→source_experience_id, publisher_id→created_by_agent_id, publisher_role→applicable_roles, effectiveness→effectiveness_score）

## 任务 2：Prompt 文件化 ✓

### 创建的文件

1. **api/domain/prompt_loader.py**
   - 从 api/domain/prompts/ 目录加载 markdown 格式的 prompt 文件
   - 支持变量替换（使用 {{variable}} 语法）
   - 支持缓存机制
   - 提供 list_prompts() 和 clear_cache() 工具函数

2. **Prompt 文件（11 个）**

   **DM 类（4 个）**
   - `api/domain/prompts/dm/intro.md` - DM 开场介绍
   - `api/domain/prompts/dm/hint.md` - DM 分级提示
   - `api/domain/prompts/dm/reveal.md` - DM 真相揭示
   - `api/domain/prompts/dm/review.md` - DM 复盘总结

   **Companion 类（3 个）**
   - `api/domain/prompts/companion/roleplay.md` - AI 角色扮演
   - `api/domain/prompts/companion/evidence_reaction.md` - 证物反应
   - `api/domain/prompts/companion/intent_generation.md` - 行动意图生成

   **Safety 类（2 个）**
   - `api/domain/prompts/safety/anti_spoiler.md` - 防剧透规则
   - `api/domain/prompts/safety/role_visibility.md` - 角色可见性规则

   **Assistant 类（1 个）**
   - `api/domain/prompts/assistant/recommend_script.md` - 剧本推荐

   **Review 类（1 个）**
   - `api/domain/prompts/review/evaluation.md` - 复盘评分

### Prompt 内容来源

所有 prompt 内容均从以下文件中提取：
- `api/agents/game_engine.py` - PHASE_CONFIG 中的 phase_prompt
- `api/llm/llm_service.py` - 各种 PROMPT 常量
- `api/orchestrator.py` - 系统 prompt
- `api/capsules/dm_evolution_service.py` - DM 评分 prompt
- `api/domain/role_visibility.py` - 角色可见性规则

## 文件清单

```
evo-murder-game/
├── scripts/
│   ├── migrate_legacy_data.py          # 数据迁移脚本
│   └── validate_migration.py           # 数据校验脚本
└── api/domain/
    ├── prompt_loader.py                # Prompt 加载器
    └── prompts/
        ├── dm/
        │   ├── intro.md
        │   ├── hint.md
        │   ├── reveal.md
        │   └── review.md
        ├── companion/
        │   ├── roleplay.md
        │   ├── evidence_reaction.md
        │   └── intent_generation.md
        ├── safety/
        │   ├── anti_spoiler.md
        │   └── role_visibility.md
        ├── assistant/
        │   └── recommend_script.md
        └── review/
            └── evaluation.md
```

## 使用说明

### 数据迁移

```bash
# 执行迁移
python scripts/migrate_legacy_data.py

# 校验迁移结果
python scripts/validate_migration.py
```

### Prompt 加载

```python
from api.domain.prompt_loader import load_prompt, list_prompts

# 加载 prompt
prompt = load_prompt("dm", "intro")

# 带变量替换
prompt = load_prompt("dm", "hint", phase="investigation", level=2, level_name="遗漏信息")

# 列出所有可用 prompt
all_prompts = list_prompts()
print(all_prompts)
```

## 特性

- ✓ 所有文件使用 UTF-8 编码
- ✓ Prompt 文件内容使用中文
- ✓ 从现有代码中提取实际的 prompt 内容
- ✓ 支持幂等迁移（可重复执行）
- ✓ 自动备份数据库
- ✓ 详细的迁移统计和校验报告
