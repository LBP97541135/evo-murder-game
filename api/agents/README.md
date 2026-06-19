# api/agents/ · README

## 职责
多Agent编排系统——管理 DM-Agent、陪玩 Agent、个人助手 Agent 的注册、角色分配、Session 创建、任务调度和进化循环。

核心概念：
- **AgentNode**：一个 Agent 在 EvoMap 网络中的实例，有自己的 node_id、constitution、identity_doc
- **AgentOrchestrator**：编排器，管理一组 Agent 的生命周期和协作
- **AgentRole**：角色枚举（DM/陪玩/助手）
- **AGENT_TEMPLATES**：每种角色的默认 constitution 和 identity_doc 模板

## 文件清单
| 文件 | 说明 |
|------|------|
| `agent_orchestrator.py` | AgentNode类 + AgentOrchestrator类 + AgentRole枚举 + AGENT_TEMPLATES模板 |
| `__init__.py` | 模块导出 |

## Agent 角色体系

| 角色 | 前缀 | EvoMap domains | 核心职责 | 信息权限 |
|------|------|---------------|---------|---------|
| DM | `DM-` | hosting, narrative-control, rule-enforcement | 主持游戏、控制节奏、防剧透 | 可读完整真相 |
| Companion | `CP-` | role-playing, inference, interaction, performance | 扮演角色、推理、互动 | 只读角色可见信息 |
| Assistant | `AS-` | user-profiling, recommendation, tag-generation | 用户画像、推荐、标签 | 可读用户全部游玩记录 |

## 进化机制

```
每局结束后：
  1. Memory record → 记录经验（signals + score + summary）
  2. 自评 → 生成结构化反思
  3. 可选：update_constitution / update_identity_doc → 改写行为规则

下一局开始前：
  1. Memory recall → 召回历史经验
  2. fetch社区Gene → 获取更好的策略
  3. 基于进化后的 constitution 行动
```

## 当前需求
- [ ] 实际注册 Agent 到 EvoMap（测试 hello 端点）
- [ ] 实现局后自评的 LLM 生成（当前自评摘要是硬编码的，应该让 LLM 生成）
- [ ] 实现 constitution 自动改写逻辑（基于 Memory recall 的经验，LLM 生成新 constitution）
- [ ] 添加 Agent 状态持久化（当前只在内存中，重启丢失）
- [ ] 实现 Agent 之间的信息隔离路由（SafeActor 过滤在 session/message 中）

## 进度
- ✅ AgentNode 类（注册/心跳/进化/记忆）
- ✅ AgentOrchestrator 类（批量注册/Session/广播/定向/自评）
- ✅ AgentRole 枚举 + AGENT_TEMPLATES 模板
- ✅ 基础进化框架（Memory record + constitution 更新）

## 疑问
- Agent 注册后 node_secret 只显示一次——需要持久化到数据库还是文件？
- 多个 Companion Agent 在同一 Session 中如何避免抢话和重复？（需要自研协调逻辑）
- DM-Agent 在 Council 中如何自动参与五阶段审议？（需要监听 deliberation 事件）
