# web/src/providers/ · README

## 职责
全局状态管理——使用 constate 库创建 React Context，管理游戏核心状态、会话ID、剧本数据、Agent列表。
所有页面和组件通过 `useMystery()` / `useSession()` / `useScript()` / `useAgent()` 读取和更新状态。

## 文件清单
| 文件 | 说明 |
|------|------|
| `contexts.tsx` | 4个Context的定义（MysteryContext / SessionContext / ScriptContext / AgentContext） |

## Context 详情

| Context | Hook | 管理内容 | 持久化 |
|---------|------|---------|--------|
| **MysteryProvider** | `useMystery()` | globalStory, actors[], currentActorId | localStorage（后续） |
| **SessionProvider** | `useSession()` | sessionId | localStorage（已有） |
| **ScriptProvider** | `useScript()` | script, scripts[], loadScript, saveScript | 后端DB同步 |
| **AgentProvider** | `useAgent()` | agents[], currentPhase | API刷新 |

## 当前需求
- [ ] MysteryContext 补充 actors 的 localStorage 持久化（参考ai-murder-mystery的mysteryContext）
- [ ] SessionContext 补充 session 恢复逻辑（页面刷新后恢复上次session）
- [ ] ScriptContext 补充后端同步逻辑（loadScript → API调用 + 本地缓存）
- [ ] AgentContext 补充自动心跳（注册的Agent每5分钟发送heartbeat）
- [ ] 补充 EvidenceContext（证据状态管理）
- [ ] 补充 NotesContext（推理笔记状态管理）

## 进度
- ✅ 4个基础Context骨架完成
- ✅ constate 使用模式统一
- ✅ SessionContext 的 sessionId localStorage持久化
- 🔲 数据持久化完善
- 🔲 Evidence/Notes Context

## 疑问
- constate 在 React 18 StrictMode 下是否有重复渲染问题？（ai-murder-mystery中用了同样方案，实测无问题）
- 是否需要 Redux/Zustand 替代 constate？——当前状态复杂度不高，constate够用
