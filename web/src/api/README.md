# web/src/api/ · README

## 职责
API调用封装层——所有与后端交互的 HTTP 请求都在这里，页面和组件不直接调用 fetch。
包括：AI推理调用、Agent管理、游戏Session、进化Memory、SafeActor信息隔离。

## 文件清单
| 文件 | 说明 |
|------|------|
| `invoke.ts` | 所有API封装：AI调用/Agent注册/列表/心跳/进化/Session/Memory/SafeActor |

## 核心函数

| 函数 | 用途 |
|------|------|
| `invokeAI(req)` | AI三层管道调用（POST /invoke） |
| `invokeAIStream(req, onChunk, onDone)` | 流式SSE调用（占位，待实现） |
| `registerAgent(role, name, model)` | 注册Agent到EvoMap（POST /agents/register） |
| `listAgents()` | 列出所有Agent（GET /agents/list） |
| `heartbeatAgent(agentKey)` | 心跳保活 |
| `evolveAgent(agentKey, type, content)` | 进化更新constitution/identity_doc |
| `createGameSession(scriptId, topic)` | 创建游戏Session |
| `broadcastMessage(sessionId, ...)` | Session内广播消息 |
| `postGameReflection(sessionId, result)` | 局后自评 |
| `recordMemory(nodeId, signals, ...)` | 记录经验到EvoMap Memory |
| `recallMemory(nodeId, signals, limit)` | 召回历史经验 |
| `memoryStatus(agentKey)` | 查看记忆概况 |
| `createSafeActorList(actors)` | **核心隔离**——过滤secret/violation字段 |

## 当前需求
- [ ] 实现流式SSE调用（invokeAIStream）
- [ ] 补充剧本CRUD API（saveScriptToDB / getScriptsFromDB / deleteScriptFromDB）
- [ ] 补充证据API（createEvidence / presentEvidence / combineEvidences）
- [ ] 补充图像生成API（generateAvatar / generateCover / generateBackground）
- [ ] 补充Council API（councilPropose / dialog）

## 进度
- ✅ 核心API框架完成（6大域：AI/Agent/Session/Memory/SafeActor/通用HTTP工具）
- ✅ SafeActor信息隔离函数
- ✅ 通用post/get工具函数
- 🔲 流式SSE（占位）
- 🔲 剧本CRUD
- 🔲 证据系统
- 🔲 图像生成

## 疑问
- 流式SSE如何实现？参考 ai-murder-mystery 的 web/src/api/invoke.ts 里的 EventSourceNative 实现
- Mantine UI 的 API_URL 配置——开发环境和生产环境的URL如何切换？
