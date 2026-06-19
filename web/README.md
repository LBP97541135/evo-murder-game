# web/ · README

## 职责
前端 Web 应用，基于 React 18 + TypeScript + Mantine UI。负责：
- 剧本库浏览与搜索
- 游戏主界面（角色对话、线索展示、推理提交）
- Agent 配置面板（注册Agent、查看状态）
- 进化时间线展示（constitution改写历史、Memory记录）
- 状态管理（constate: MysteryContext/SessionContext/ScriptContext/AgentContext）

## 当前需求
- [ ] 实现游戏主界面（角色对话区 + 线索面板 + 笔记面板）
- [ ] 实现流式对话输出
- [ ] 对接后端所有 API（Agent注册/Session/Memory）
- [ ] 剧本库完整功能（搜索/筛选/创建/导入）
- [ ] 进化时间线数据对接（从后端API获取）

## 进度
- ✅ 项目骨架搭建（package.json/tsconfig/index.html/App.tsx）
- ✅ 类型定义（types/index.ts: Actor/SafeActor/Script/Character/AgentNodeInfo/GameSession/EvolutionRecord）
- ✅ API层封装（api/invoke.ts: AI调用/Agent注册/Session/Memory/SafeActor）
- ✅ 状态管理（providers/contexts.tsx: 4个Context）
- ✅ 路由配置（App.tsx: library/play/agents/evolution）
- ✅ 剧本库页面骨架（ScriptLibrary.tsx）
- ✅ 游戏页面骨架（GamePage.tsx）
- ✅ Agent配置面板骨架（AgentPanel.tsx）
- ✅ 进化时间线骨架（EvolutionTimeline.tsx）
- 🔲 角色对话组件（Actor.tsx）
- 🔲 线索/证据系统
- 🔲 推理提交组件（选凶手→选动机→验证）
- 🔲 游戏复盘界面
- 🔲 流式对话体验

## 疑问
- Mantine UI v7 的 API 是否与 v6 有重大差异？需确认版本兼容性
- constate 在 React 18 StrictMode 下是否有问题？
- 流式 SSE 的前端实现需要参考 ai-murder-mystery 的 invoke.ts stream 实现
