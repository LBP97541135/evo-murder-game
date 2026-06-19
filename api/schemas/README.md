# api/schemas/ · README

## 职责
Pydantic 数据模型——定义所有 API 端点的请求和响应格式。
这些模型同时用于 FastAPI 的自动文档生成和请求校验。

## 文件清单
| 文件 | 说明 |
|------|------|
| `invoke_types.py` | 所有请求/响应模型 |
| `__init__.py` | 模块导出 |

## 核心模型

| 模型 | 用途 | 关键字段 |
|------|------|---------|
| `Actor` | 完整角色信息 | id, name, bio, secret, violation, 角色标记 |
| `SafeActor` | 安全角色信息（过滤敏感字段） | 无 secret/violation 字段 |
| `LLMMessage` | 对话消息 | role, content |
| `InvocationRequest` | AI调用请求 | actor, chat_messages, all_actors |
| `InvocationResponse` | AI调用响应 | original, critique, refined, final_response |
| `AgentRegistrationRequest` | Agent注册请求 | role, name, model |
| `AgentRegistrationResponse` | Agent注册响应 | node_id, node_secret, claim_url |
| `GameSessionRequest` | 创建游戏Session | script_id, topic |
| `MemoryRecordRequest` | 记录经验 | node_id, signals, score, summary |
| `MemoryRecallRequest` | 召回经验 | node_id, signals, limit |
| `EvolutionUpdateRequest` | Agent进化更新 | update_type, new_content |

## SafeActor 信息隔离

这是从 ai-murder-mystery 复用的核心机制：

```
Actor（完整）  → 发给角色自己 + DM
  包含: secret, violation, background_image

SafeActor（安全）  → 发给其他角色 + 前端展示
  不包含: secret, violation, background_image
```

**为什么重要**：如果 Companion Agent A 能看到 Agent B 的 secret，那整个推理游戏的逻辑就崩了。

## 当前需求
- [ ] 补充证据相关模型（Evidence/EvidenceReaction，从 ai-murder-mystery 复用）
- [ ] 补充剧本 CRUD 模型（ScriptCreateRequest/ScriptUpdateRequest）
- [ ] 补充 Council 审议模型（CouncilProposeRequest/DialogRequest）
- [ ] 补充图像生成模型（AvatarGenerateRequest/CoverGenerateRequest）

## 进度
- ✅ 核心请求/响应模型完成
- ✅ SafeActor 信息隔离机制
- ✅ Agent 注册/进化模型

## 疑问
- EvolutionUpdateRequest 的 node_id 字段是否必要？（可以从 URL path 中的 agent_key 推断）
- AgentRegistrationResponse 中是否应该返回 node_secret？（安全风险——但注册时确实需要告知）
