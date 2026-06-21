# web/ 目录 README

## 职责

`web/` 是进化酒馆的主前端应用，基于 React 18、TypeScript、
Mantine UI 7、React Router 7 和 Create React App。

当前版本是暗黑工业剧场风格的静态可交互原型，覆盖剧本选择、游戏舞台、
Agent 阵容和个人助手四条主要用户路径。视觉方向参考 `figma-make/`，
但主应用继续使用 Mantine，不直接复用参考工程的 Tailwind 和 Radix 组件。

## 目录结构

```text
web/
├── figma-make/             # 独立的 Figma Make/Vite 视觉参考工程
├── public/                 # CRA 静态资源与 HTML 入口
├── src/
│   ├── api/                # 后端 API 调用封装
│   ├── components/         # 可复用业务组件预留目录
│   ├── constants/          # 常量预留目录
│   ├── pages/              # 四个主页面与共享 StudioShell
│   ├── providers/          # constate 全局状态
│   ├── types/              # TypeScript 类型
│   ├── utils/              # 工具函数预留目录
│   ├── App.tsx             # Mantine 主题、Provider 和路由
│   ├── index.tsx           # React 入口及 Mantine 基础样式入口
│   └── styles.css          # 全局字体、背景、卡片和氛围样式
├── package.json
└── tsconfig.json
```

## 启动与构建

```bash
cd web
npm install
npm start
```

开发服务器默认地址为 `http://localhost:3000`，前端 API 通过 `package.json`
的 `proxy` 代理到 `http://localhost:8000`。`npm start` 无需额外环境变量，
跨平台（Windows/macOS/Linux）直接运行。

如需自定义后端地址：

```bash
# macOS / Linux
REACT_APP_API_URL=http://localhost:8000 npm start

# Windows PowerShell
$env:REACT_APP_API_URL="http://localhost:8000"; npm start
```

生产构建：

```powershell
cd web
npm run build
```

## 应用入口

- `src/index.tsx` 必须导入 `@mantine/core/styles.css`。缺少该入口时，
  Mantine 组件只会保留不完整的基础外观。
- `src/App.tsx` 创建暗色 Mantine 主题，定义红色强调色、正文和标题字体，
  并挂载 Agent、Script、Session、Mystery 四层 Provider。
- `src/styles.css` 提供暗色渐变、网格纹理、玻璃背景、工业卡片、
  Hero 和等宽标签等跨页面样式。
- 全局字体从 Google Fonts 加载；离线环境会回退到 Georgia 和 monospace。

## 页面路由

| 路由 | 页面 | 当前能力 |
|------|------|----------|
| `/` | 重定向 | 自动跳转到 `/library` |
| `/library` | 剧本库 | 搜索、题材与难度筛选、推荐流、详情和 Agent 适配 |
| `/play/:id` | 游戏主界面 | 模式切换、场景舞台、玩家互动、DM 节奏和复盘 |
| `/agents` | Agent 广场 | 陪玩/DM 切换、搜索筛选、详情、阵容与操作入口 |
| `/evolution` | 个人助手 | 用户画像、偏好标签、推荐、游玩总结和开局建议 |

页面细节见 [src/pages/README.md](src/pages/README.md)。

## 视觉规范

- 背景以黑红、炭灰和旧纸色为主，红色只用于关键状态和主要操作。
- 标题使用 `Cinzel Decorative`，正文使用 `Crimson Pro`，
  数据标签使用 `JetBrains Mono`。
- 页面使用统一的 `StudioShell`、Hero、统计面板和工业卡片。
- 卡片强调边框、内高光、深阴影和轻度毛玻璃，不使用纯色平铺。
- 桌面端提供完整顶部导航；窄屏通过页面内导航保持主要路由可达。

## 数据状态

当前四个页面主要使用组件内定义的演示数据，用于验证信息架构和视觉设计。
`src/api/`、`src/providers/` 和类型层仍然保留，但新版页面尚未全部接入真实 API。
因此按钮、筛选和面板切换可以交互，注册、匹配、聊天和持久化等业务流程仍需后续对接。

## 参考工程

`figma-make/` 是独立 Vite 工程，只承担视觉参考和设计溯源：

- 不在 `src/` 内，不会被 CRA 和 TypeScript 主工程扫描。
- 有自己的 `package.json`、入口、样式和组件依赖。
- 不应从主应用直接 import 其中的源码。
- 修改参考工程时，应在 `figma-make/` 内单独安装依赖和运行。

## 当前进度

- [x] 修复 Mantine 全局样式入口
- [x] 建立暗黑工业剧场主题和全局样式
- [x] 建立四个主路由及共享布局壳
- [x] 完成剧本库静态交互原型
- [x] 完成游戏舞台静态交互原型
- [x] 完成 Agent 广场静态交互原型
- [x] 完成个人助手静态交互原型
- [x] 将 Figma Make 工程隔离到主应用源码目录之外
- [x] 增加浏览器兼容目标和 Windows 启动脚本
- [x] 主应用生产构建通过
- [ ] 将页面演示数据替换为后端数据
- [ ] 完成聊天、匹配、收藏、邀请和复盘持久化
- [ ] 补充页面级测试与移动端视觉回归

## 已知限制

- `npm start` 已改为跨平台兼容（直接 `react-scripts start`），不再依赖 Windows 专用语法
- 外部封面图片和 Google Fonts 需要网络访问
- `figma-make/` 未安装依赖时无法直接执行 `npm run dev` 或 `npm run build`
