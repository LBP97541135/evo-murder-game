# web/src/pages/ · README

## 职责
页面级组件——每个文件对应一个路由页面，是用户看到的完整界面。
页面组件负责组合子组件、调用API、管理页面级状态。

## 文件清单
| 文件 | 路由 | 说明 |
|------|------|------|
| `ScriptLibrary.tsx` | `/library` | 剧本库——浏览/搜索/筛选剧本 |
| `GamePage.tsx` | `/play/:id` | 游戏主界面——角色对话/线索/推理（骨架） |
| `AgentPanel.tsx` | `/agents` | Agent配置——注册Agent/查看状态 |
| `EvolutionTimeline.tsx` | `/evolution` | 进化时间线——constitution改写/Memory记录（骨架） |

## 页面功能详情

### ScriptLibrary（P0，部分实现）
- 剧本网格展示（SimpleGrid 3列）
- 搜索栏（TextInput）
- 难度/题材筛选（Select）
- 点击剧本 → 进入游戏
- 🔲 热门剧本/新上线剧本排序
- 🔲 AI质检评分展示

### GamePage（骨架，P0 待实现）
- 🔲 左侧：角色选择 + 对话界面（Actor组件）
- 🔲 右侧：线索面板 + 笔记面板（TabbedRightPanel）
- 🔲 底部：推理提交（选凶手→选动机→验证）
- 🔲 DM控制区（阶段切换/提示发放）
- 🔲 游戏复盘界面

### AgentPanel（部分实现）
- Agent注册表单（角色/名称/注册按钮）
- 已注册Agent列表（刷新/角色Badge/状态）
- 🔲 Agent详情展开（constitution/identity_doc/记忆概况）
- 🔲 心跳状态实时展示
- 🔲 Agent进化参数配置

### EvolutionTimeline（骨架，P1 待实现）
- 🔲 constitution 改写历史时间线
- 🔲 Memory 记录卡片
- 🔲 Gene/Capsule 发布记录
- 🔲 从后端API获取数据

## 当前需求
- [ ] GamePage 完整实现（这是最核心的页面）
- [ ] ScriptLibrary 对接后端API获取剧本列表
- [ ] AgentPanel 对接后端API实现实际注册
- [ ] EvolutionTimeline 对接后端API获取进化记录

## 进度
- ✅ 4个页面骨架完成
- ✅ ScriptLibrary 基础UI（网格+搜索+筛选）
- ✅ AgentPanel 注册表单 + Agent列表
- 🔲 GamePage 完整实现
- 🔲 EvolutionTimeline 数据对接

## 疑问
- GamePage 的布局——参考ai-murder-mystery的Home.tsx（左侧角色列表+中间对话+右侧线索面板）
- 是否需要 Mantine AppShell 做全局导航栏？（Header + 侧边栏）
