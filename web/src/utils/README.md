# web/src/utils/ · README

## 职责
工具函数——纯逻辑的辅助函数，不涉及UI渲染和API调用。
被 components/ 和 pages/ 引用。

## 当前状态
⚠️ **目录为空**——所有工具函数尚未实现。

## 预期文件清单（按优先级排序）

### P0 — 核心工具
| 文件 | 说明 | 参考（ai-murder-mystery） |
|------|------|--------------------------|
| `safeActorInfo.ts` | SafeActor信息隔离——createSafeActorList/validateSafeActorList | `web/src/utils/safeActorInfo.ts` |
| `storageManager.ts` | localStorage管理——CRUD/清理/容量计算 | `web/src/utils/storageManager.ts` |

### P1 — 剧本管理
| 文件 | 说明 |
|------|------|
| `scriptManager.ts` | 剧本localStorage CRUD + 导入导出JSON |
| `evidenceManager.ts` | 证据localStorage CRUD + 状态追踪 |
| `noteManager.ts` | 笔记localStorage CRUD + AI摘要生成 |
| `avatarUtils.ts` | 角色头像URL构建/缓存 |

### P2 — 辅助工具
| 文件 | 说明 |
|------|------|
| `formatTime.ts` | 时间格式化 |
| `roleInteraction.ts` | 角色交互提示生成 |
| `roleUtils.ts` | 通用角色判断工具 |
| `streamingJsonParser.ts` | 流式JSON解析（AI生成剧本时用） |

## 当前需求
- [ ] 实现 safeActorInfo.ts（最核心，信息隔离的前端实现）
- [ ] 实现 storageManager.ts（localStorage管理）
- [ ] 实现 scriptManager.ts（剧本CRUD）
- [ ] 实现 evidenceManager.ts（证据CRUD）

## 进度
- 🔲 所有工具函数待实现
- ✅ safeActorInfo的逻辑已内联在 `api/invoke.ts` 的 `createSafeActorList()` 中（后续应抽取到utils/）

## 疑问
- safeActorInfo 目前在 api/invoke.ts 里——是否应该抽取到 utils/safeActorInfo.ts？
  → 建议：是的，utils/ 是更合理的位置，api层只管HTTP调用
