# web/src/components/ · README

## 职责
可复用UI组件——页面内部的具体交互组件，被 pages/ 引用。
每个组件负责一块具体的UI功能，通过 props 接收数据，通过 Context 或 API 调用更新状态。

## 当前状态
⚠️ **目录为空**——所有组件尚未实现，待从 pages/ 的骨架逐步拆分出来。

## 预期组件清单（按优先级排序）

### P0 — 游戏核心组件
| 组件 | 说明 | 参考（ai-murder-mystery） |
|------|------|--------------------------|
| `Actor.tsx` | 角色对话组件——流式AI对话+角色头像+消息列表 | `web/src/components/Actor.tsx` |
| `ChatMessage.tsx` | 单条消息气泡——Markdown渲染+角色标识 | `web/src/components/ChatMessage.tsx` |
| `ActorSidebar.tsx` | 角色侧边栏——列出所有角色+当前选中 | `web/src/components/ActorSidebar.tsx` |
| `TabbedRightPanel.tsx` | 右侧标签面板——线索库+笔记切换 | `web/src/components/TabbedRightPanel.tsx` |
| `MultipleChoiceGame.tsx` | 推理提交——选凶手→选动机→验证 | `web/src/components/MultipleChoiceGame.tsx` |
| `IntroModal.tsx` | 游戏开场模态框——展示背景故事 | `web/src/components/IntroModal.tsx` |
| `EndModal.tsx` | 游戏结局模态框——展示真相 | `web/src/components/EndModal.tsx` |
| `Header.tsx` | 顶部导航栏——Logo+页面链接+当前剧本名 | `web/src/components/Header.tsx` |

### P0 — 证据组件子目录 `evidence/`
| 组件 | 说明 |
|------|------|
| `EvidenceCard.tsx` | 单条证据卡片 |
| `EvidenceLibraryPanel.tsx` | 证据库面板（筛选+搜索） |
| `EvidenceSelectorPanel.tsx` | 选择并向角色出示证据 |
| `EvidenceDetailModal.tsx` | 证据详情模态框 |

### P1 — Agent组件
| 组件 | 说明 |
|------|------|
| `AgentCard.tsx` | Agent卡片——头像+名称+角色+状态 |
| `AgentDetailModal.tsx` | Agent详情模态框——constitution/记忆/进化历史 |
| `AgentRegisterForm.tsx` | Agent注册表单（从AgentPanel拆出） |

### P2 — 进化组件
| 组件 | 说明 |
|------|------|
| `EvolutionCard.tsx` | 单条进化记录卡片 |
| `ConstitutionDiff.tsx` | constitution改写对比（旧→新） |

## 当前需求
- [ ] 从 ai-murder-mystery 复用并适配 Actor.tsx（最核心）
- [ ] 复用 ChatMessage.tsx（Markdown渲染）
- [ ] 复用 ActorSidebar.tsx（角色列表）
- [ ] 复用 Header.tsx（导航栏）
- [ ] 复用 TabbedRightPanel.tsx
- [ ] 实现流式对话体验（SSE）

## 进度
- 🔲 所有组件待实现

## 疑问
- 是否直接从 ai-murder-mystery 复制组件代码然后改造？还是从零写？
  → 建议：核心组件（Actor/ChatMessage/Header）直接复用改适配，游戏特定组件从零写
- 证据组件是否需要先做？→ P0优先级，游戏核心体验依赖证据交互
