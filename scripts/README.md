# scripts/ · README

## 职责
工具脚本目录，存放：
- CI/CD 检查脚本
- Agent批量注册脚本
- 剧本数据迁移脚本
- EvoMap API测试脚本
- 数据库初始化/清理脚本
- 剧本生成辅助脚本

## 文件清单
| 文件 | 说明 |
|------|------|
| `check_readme_sync.py` | CI检查脚本——如果代码变更但README未同步，则拒绝合并 |

## 当前需求
- [ ] Agent批量注册脚本（一键注册DM+若干陪玩Agent）
- [ ] EvoMap API连通性测试脚本
- [ ] 剧本数据导入脚本（从JSON文件导入到数据库）

## 进度
- ✅ check_readme_sync.py — README同步检查脚本完成
  - 规则：代码变更但README未更新 → 拒绝合并
  - 覆盖目录：api/ 及其7个子目录 + web/ + docs/ + scripts/
  - 忽略：纯README变更、纯__init__.py变更、纯配置文件变更

## 疑问
- 是否需要从 ai-murder-mystery 的示例剧本导入数据？
