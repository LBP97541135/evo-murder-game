# web/ · README

## 职责
前端 Web 应用，基于 React 18 + TypeScript + Mantine UI。
负责所有用户可见的界面：剧本库、游戏主界面、Agent配置、进化时间线。

## 目录结构

```
web/
├── package.json            ← 依赖和脚本
├── tsconfig.json           ← TypeScript配置
│
├── public/                 ← 静态资源（不经编译）
│   ├── index.html          ← HTML入口
│   ├── favicon.svg         ← 酒馆Logo
│   └── README.md           ← 需求/进度/疑问
│
├── src/
│   ├── App.tsx             ← 应用入口 + 路由定义
│   ├── index.tsx           ← React渲染入口
│   ├── constants.ts        ← API_URL等根级常量
│   │
│   ├── api/                ← API调用封装
│   │   ├── invoke.ts       ← 所有后端API封装（AI/Agent/Session/Memory/SafeActor）
│   │   └── README.md
│   │
│   ├── types/              ← TypeScript类型定义
│   │   ├── index.ts        ← 所有类型（Actor/SafeActor/Script/Character/Agent/GameSession/Evolution）
│   │   └── README.md
│   │
│   ├── providers/          ← 状态管理（constate Context）
│   │   ├── contexts.tsx    ← 4个Context（Mystery/Session/Script/Agent）
│   │   └── README.md
│   │
│   ├── pages/              ← 页面组件
│   │   ├── ScriptLibrary.tsx ← 剧本库
│   │   ├── GamePage.tsx    ← 游戏主界面（骨架）
│   │   ├── AgentPanel.tsx  ← Agent配置面板
│   │   ├── EvolutionTimeline.tsx ← 进化时间线（骨架）
│   │   └── README.md
│   │
│   ├── components/         ← 可复用UI组件（⚠️ 目录为空，待实现）
│   │   └── README.md       ← 预期组件清单 + 优先级
│   │
│   ├── constants/          ← 常量定义（⚠️ 目录为空，待迁移）
│   │   └── README.md
│   │
│   ├── utils/              ← 工具函数（⚠️ 目录为空，待实现）
│   │   └── README.md       ← 预期工具清单 + 优先级
│   │
│   └── README.md           ← 本文件
│
└── README.md               ← 本文件
```

## 当前需求
- [ ] 实现游戏主界面 GamePage（最核心）
- [ ] 从 ai-murder-mystery 复用核心组件（Actor/ChatMessage/Header）
- [ ] 对接后端所有API
- [ ] 实现流式对话输出
- [ ] 实现证据系统UI

## 进度
- ✅ 项目骨架搭建
- ✅ 类型定义完整
- ✅ API层封装
- ✅ 状态管理（4个Context）
- ✅ 路由配置（4个页面）
- ✅ 每个子目录都有 README
- 🔲 组件实现（components/为空）
- 🔲 工具函数实现（utils/为空）
- 🔲 流式SSE
- 🔲 证据系统

## 疑问
- GamePage布局参考 ai-murder-mystery 的 Home.tsx
- 是否需要 Mantine AppShell 做全局导航？
