# web/src/constants/ · README

## 职责
常量定义——集中存放所有前端硬编码的常量值，避免散落在各组件中。

## 当前状态
⚠️ **目录为空**——常量目前放在 `src/constants.ts`（根级文件），后续迁移到此目录。

## 预期文件清单
| 文件 | 说明 |
|------|------|
| `api.ts` | API_URL 等API相关常量 |
| `fieldExplanations.ts` | 剧本编辑器各字段的悬浮提示说明（参考ai-murder-mystery） |
| `roleTypes.ts` | 角色类型枚举常量（suspect/witness/victim/killer/assistant/partner） |
| `agentRoles.ts` | Agent角色常量（dm/companion/assistant）+ 默认constitution模板 |
| `theme.ts` | UI主题常量（颜色/间距/字号） |

## 当前需求
- [ ] 将 `src/constants.ts` 迁移到 `src/constants/api.ts`
- [ ] 补充 `fieldExplanations.ts`（从ai-murder-mystery复用）
- [ ] 补充 `roleTypes.ts` 和 `agentRoles.ts`

## 进度
- ✅ `src/constants.ts` 已有 API_URL 定义
- 🔲 迁移到目录内分文件
- 🔲 补充更多常量

## 疑问
- 剧本编辑器的字段提示说明是否需要？（如果后续做编辑器就需要）
