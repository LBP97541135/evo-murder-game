# web/src/types/ · README

## 职责
TypeScript 类型定义——所有前端使用的类型集中在此，其他模块通过 import 引用。
这是整个前端项目的"契约层"，API层、组件层、状态层都依赖这里的类型。

## 文件清单
| 文件 | 说明 |
|------|------|
| `index.ts` | 所有类型定义（Actor/SafeActor/Script/Character/AgentNodeInfo/GameSession/EvolutionRecord等） |

## 核心类型

| 类型 | 用途 | 关键字段 |
|------|------|---------|
| `Actor` | 完整角色信息 | id, name, bio, **secret**, **violation**, 角色标记 |
| `SafeActor` | 安全角色信息（隔离后） | 无secret/violation字段 |
| `LLMMessage` | 对话消息 | role, content |
| `Script` | 剧本 | title, globalStory, characters[], difficulty, theme |
| `Character` | 角色 | name, bio, personality, secret, violation, 角色标记 |
| `ScriptSettings` | 剧本设置 | theme, difficulty, duration, playerCount |
| `AgentNodeInfo` | Agent节点展示信息 | key, name, role, nodeId, registered |
| `AgentRegistration` | Agent注册响应 | nodeId, nodeSecret, claimUrl |
| `GameSession` | 游戏会话 | sessionId, participants, status, currentPhase |
| `EvolutionRecord` | 进化记录 | signals, score, summary, updateType, oldContent, newContent |
| `EvolutionUpdate` | 进化更新请求 | nodeId, updateType, newContent |

## 当前需求
- [ ] 补充证据类型（Evidence / EvidenceReaction / EvidenceDiscovery / EvidenceCombination，参考ai-murder-mystery）
- [ ] 补充笔记类型（Note / NoteFilter）
- [ ] 补充Council类型（CouncilProposal / DialogContent）
- [ ] 补充资产搜索类型（AssetSearchResult / GeneAsset / CapsuleAsset）

## 进度
- ✅ 基础类型体系完成（11个核心类型）
- ✅ Actor/SafeActor 双模型（信息隔离核心）
- ✅ Agent相关类型（注册/节点/进化）
- ✅ 游戏会话类型

## 疑问
- Character 和 Actor 的字段基本重复——是否应该合并？（目前Character用于剧本定义，Actor用于运行时，语义不同但字段相同）
- EvolutionRecord 的 updateType 是否需要更多选项？（当前只有constitution/identity_doc）
