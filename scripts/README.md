# scripts/ · README

## 职责
工具脚本目录，存放：
- CI/CD 检查脚本
- GitHub 分支保护设置脚本
- Agent批量注册脚本
- 剧本数据迁移脚本
- EvoMap API测试脚本
- 数据库初始化/清理脚本

## 文件清单
| 文件 | 说明 |
|------|------|
| `check_readme_sync.py` | CI检查——代码变更但README未同步 → 拒绝合并（PR模式） / 发警告（push模式） |
| `setup_branch_protection.py` | 设置GitHub main分支保护规则——禁止直接push，强制走PR |

## 当前需求
- [ ] 运行 setup_branch_protection.py 或手动设置分支保护（⚠️ 必须做！否则CI无法阻止直接push）
- [ ] Agent批量注册脚本（一键注册DM+若干陪玩Agent）
- [ ] EvoMap API连通性测试脚本
- [ ] 剧本数据导入脚本（从JSON文件导入到数据库）

## 进度
- ✅ check_readme_sync.py — README同步检查完成
  - PR模式：代码变更但README未更新 → ❌ 阻断合并
  - Push模式：代码变更但README未更新 → ⚠️ 警告（无法阻止，需靠分支保护）
  - 覆盖目录：api/ 及其7个子目录 + web/ + docs/ + scripts/
  - 忽略：纯README变更、纯__init__.py变更、纯配置文件变更
- ✅ setup_branch_protection.py — 分支保护设置脚本完成
  - 禁止直接push到main
  - 强制走PR，需1人approval
  - PR必须通过check-readme-sync才能合并
  - 管理员也不能绕过

## 疑问
- 分支保护规则需要 repo_admin 权限才能通过API设置——如果不方便，可以直接在GitHub网页上手动设置
- 是否需要从 ai-murder-mystery 的示例剧本导入数据？
