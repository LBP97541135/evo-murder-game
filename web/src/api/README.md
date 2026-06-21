# 前后端接口与功能对应关系

本文档记录 `api/routes` 与 `web/src` 的实际对应关系。前端统一通过
`web/src/api/invoke.ts` 访问后端，页面不直接调用 `fetch`。

## 接入原则

- 后端请求字段统一使用 snake_case，前端页面继续使用 camelCase。
- 字段转换、错误处理、查询参数和 SSE 解析集中在 `invoke.ts`。
- 后端请求失败时直接显示错误，不使用本地业务数据掩盖接口故障。
- 游戏页创建 Session 后，将 `session_id` 保存到
  `localStorage["game-session:{scriptId}"]`。
- `REACT_APP_API_URL` 控制后端地址，默认值为 `http://localhost:8000`（见 `src/constants.ts`）。

## 页面接入情况

| 前端功能 | 页面/模块 | 后端接口 | 当前状态 |
|---|---|---|---|
| 剧本列表 | `ScriptLibrary.tsx` | `GET /scripts/list` | 已接入，失败时使用 `scriptData.ts` |
| 剧本详情 | `ScriptDetailPage.tsx` | `GET /scripts/{script_id}` | 已接入，失败时使用本地详情 |
| Agent 人设广场 | `AgentPanel.tsx` | `GET /agents/personas` | 已接入，失败时使用本地 Agent |
| 创建游戏会话 | `GamePage.tsx` | `POST /game/create-session` | 确认选角时调用 |
| 游戏阶段同步 | `GamePage.tsx` | `POST /game/phase/{session_id}/force` | 页面切换阶段时调用 |
| 运行时证物读取 | `GamePage.tsx` | `GET /evidence/script/{script_id}/session/{session_id}` | 恢复已有 Session 时调用 |
| 搜证记录 | `GamePage.tsx` | `POST /evidence/create` | 随机搜证后调用 |
| 出示证物 | `GamePage.tsx` | `POST /evidence/present` | 确认出示时调用 |
| 公开/私聊记录 | `GamePage.tsx` | `POST /conversations/save` | 发送消息时调用 |
| Agent 聊天状态 | `GamePage.tsx` | `POST /game/agent-chat/{session_id}` | 公开发言时同步 |
| 推理投票 | `GamePage.tsx` | `POST /game/vote/{session_id}` | 提交投票时调用 |
| SSE AI 回复 | `invokeAIStream()` | `POST /invoke/stream` | API 层已实现，待具体 Agent 对话 UI 使用 |

## 后端接口清单

“API 层”表示已有前端函数，但暂时没有独立页面入口。“页面接入”表示已有实际 UI
调用。

### 健康检查

| 方法与路径 | 前端函数 | 状态 |
|---|---|---|
| `GET /health` | `healthCheck` | API 层 |

### AI 调用

| 方法与路径 | 前端函数 | 状态 |
|---|---|---|
| `POST /invoke/` | `invokeAI` | API 层 |
| `POST /invoke/stream` | `invokeAIStream` | API 层，SSE 已实现 |

### Agent 与人设

| 方法与路径 | 前端函数 | 状态 |
|---|---|---|
| `POST /agents/register` | `registerAgent` | API 层 |
| `GET /agents/list` | `listAgents` | API 层 |
| `POST /agents/heartbeat/{agent_key}` | `heartbeatAgent` | API 层 |
| `POST /agents/evolve/{agent_key}` | `evolveAgent` | API 层 |
| `POST /agents/personas/init` | `initPersonas` | API 层 |
| `GET /agents/personas` | `listPersonas` | 页面接入 |
| `GET /agents/personas/{persona_key}` | `getPersona` | API 层 |
| `POST /agents/personas/load` | `loadPersona` | API 层 |
| `POST /agents/personas/auto-match` | `autoMatchPersonas` | API 层 |

### 游戏会话与 Agent 状态

| 方法与路径 | 前端函数 | 状态 |
|---|---|---|
| `POST /game/create-session` | `createGameSession` | 页面接入 |
| `GET /game/phase/{session_id}` | `getGamePhase` | API 层 |
| `POST /game/phase/{session_id}/advance` | `advanceGamePhase` | API 层 |
| `POST /game/phase/{session_id}/force` | `forceGamePhase` | 页面接入 |
| `POST /game/vote/{session_id}` | `submitGameVote` | 页面接入 |
| `POST /game/broadcast/{session_id}` | `broadcastMessage` | API 层；后端参数模型建议调整 |
| `POST /game/chat-count/{session_id}` | `recordChatCount` | API 层 |
| `POST /game/reflect/{session_id}` | `postGameReflection` | API 层 |
| `POST /game/reveal/{session_id}` | `revealGame` | API 层 |
| `POST /game/reveal/{session_id}/spoiler` | `generateSpoiler` | API 层 |
| `GET /game/agent-state/{session_id}/{agent_key}` | `getAgentState` | API 层 |
| `GET /game/intents/{session_id}/{agent_key}` | `getAgentIntents` | API 层 |
| `POST /game/intents/{session_id}/{agent_key}/generate` | `generateAgentIntents` | API 层 |
| `POST /game/intents/{session_id}/{agent_key}/approve` | `approveAgentIntent` | API 层 |
| `POST /game/agent-chat/{session_id}` | `recordAgentChat` | 页面接入 |

### 剧本

| 方法与路径 | 前端函数 | 状态 |
|---|---|---|
| `GET /scripts/list` | `listScripts` | 页面接入 |
| `GET /scripts/{script_id}` | `getScript` | 页面接入 |

后端当前没有剧本新增、修改和删除路由。

### 证物与进度

| 方法与路径 | 前端函数 | 状态 |
|---|---|---|
| `GET /evidence/script/{script_id}/session/{session_id}` | `getEvidences` | 页面接入 |
| `POST /evidence/create` | `createEvidence` | 页面接入 |
| `PUT /evidence/{evidence_id}` | `updateEvidence` | API 层 |
| `POST /evidence/present` | `presentEvidence` | 页面接入 |
| `POST /evidence/combine` | `combineEvidences` | API 层 |
| `GET /evidence/{evidence_id}/presentations` | `getEvidencePresentations` | API 层 |
| `GET /evidence/progress/{session_id}` | `getGameProgress` | API 层 |
| `POST /evidence/progress/{session_id}/phase` | `updateProgressPhase` | API 层 |
| `DELETE /evidence/{evidence_id}` | `deleteEvidence` | API 层 |

### 对话

| 方法与路径 | 前端函数 | 状态 |
|---|---|---|
| `POST /conversations/save` | `saveConversation` | 页面接入 |
| `GET /conversations/session/{session_id}` | `getConversations` | API 层 |
| `DELETE /conversations/session/{session_id}` | `clearConversations` | API 层 |

### 剧透故事

| 方法与路径 | 前端函数 | 状态 |
|---|---|---|
| `POST /spoiler-stories/save` | `saveSpoilerStory` | API 层 |
| `GET /spoiler-stories/{script_id}` | `listSpoilerStories` | API 层 |
| `GET /spoiler-stories/story/{story_id}` | `getSpoilerStory` | API 层 |
| `PUT /spoiler-stories/{story_id}` | `updateSpoilerStory` | API 层 |
| `DELETE /spoiler-stories/{story_id}` | `deleteSpoilerStory` | API 层 |
| `POST /spoiler-stories/batch-delete` | `batchDeleteSpoilerStories` | API 层 |

### Memory

| 方法与路径 | 前端函数 | 状态 |
|---|---|---|
| `POST /memory/record` | `recordMemory` | API 层 |
| `POST /memory/recall` | `recallMemory` | API 层 |
| `GET /memory/status/{agent_key}` | `memoryStatus` | API 层 |

### Gene 与 Capsule

| 方法与路径 | 前端函数 | 状态 |
|---|---|---|
| `POST /capsules/genes` | `createGene` | API 层 |
| `GET /capsules/genes/{gene_id}` | `getGene` | API 层 |
| `GET /capsules/genes` | `listGenes` | API 层 |
| `POST /capsules/genes/{gene_id}/review` | `reviewGene` | API 层 |
| `POST /capsules/genes/{gene_id}/generate-capsule` | `generateCapsuleFromGene` | API 层 |
| `POST /capsules/search` | `searchCapsules` | API 层 |
| `GET /capsules/capsules/{capsule_id}` | `getCapsule` | API 层 |
| `GET /capsules/capsules` | `listCapsules` | API 层 |
| `DELETE /capsules/capsules/{capsule_id}` | `deleteCapsule` | API 层 |
| `POST /capsules/consume` | `consumeCapsules` | API 层 |
| `POST /capsules/review-and-generate` | `reviewAndGenerateCapsules` | API 层 |

## 已知契约问题

1. `POST /game/broadcast/{session_id}` 的 `payload: dict` 当前声明为普通函数参数。
   FastAPI 无法稳定地从 query string 解析任意字典，建议后端增加 Pydantic body 模型。
2. 后端游戏阶段为 `intro/investigation/voting/reveal/review`，前端展示阶段更细。
   当前通过映射和 `force` 接口同步；长期应由后端返回可配置的阶段模型。
3. 创建游戏 Session 前必须至少注册一个 Agent，否则后端返回 400，前端不会继续进入本地游戏模式。
4. `MyGamesPage` 所需的游戏 Session 列表/详情接口目前不存在，因此仍使用展示数据。
5. 用户、收藏、推荐、私聊线程、阵容持久化等功能目前没有后端接口。

## 后续接入优先级

1. 将 Agent 对话 UI 接到 `invokeAIStream`。
2. 增加后端游戏 Session 列表与恢复接口，替换 `MyGamesPage` 静态数据。
3. 在证物面板增加组合、详情更新和出示历史入口。
4. 在 Agent 页面增加注册、加载人设、自动匹配、进化与 Memory 操作入口。
5. 在进化中心增加 Gene/Capsule 的审核和管理界面。
