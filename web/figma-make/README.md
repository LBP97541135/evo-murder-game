# figma-make/ 视觉参考工程

## 职责

这是 Figma Make 导出的“剧本杀网站前端”独立代码包，原始设计文件：

https://www.figma.com/design/DZoKhzUWcXACPmwNDoAGtd/%E5%89%A7%E6%9C%AC%E6%9D%80%E7%BD%91%E7%AB%99%E5%89%8D%E7%AB%AF

本目录用于提供暗黑剧场风格的视觉参考，包括字体、色彩、剧本卡片、
导航、主视觉和内容层级。它不是 `web/src` 主应用的一部分，也不会参与
Create React App 的构建。

## 技术栈

- React 18
- Vite 6
- Tailwind CSS 4
- Radix UI / shadcn/ui 风格组件
- Lucide React
- Motion

`package.json` 中还保留了 Figma Make 生成环境提供的完整组件依赖，
当前页面并未使用其中所有依赖。

## 目录结构

```text
figma-make/
├── guidelines/             # Figma Make 生成规则模板
├── src/
│   ├── app/
│   │   ├── App.tsx         # 暗夜剧场单页参考实现
│   │   └── components/     # Figma 图片组件与 UI 组件集合
│   ├── styles/             # 字体、Tailwind 和主题变量
│   └── main.tsx            # Vite 入口
├── ATTRIBUTIONS.md         # shadcn/ui 与 Unsplash 授权说明
├── package.json
└── vite.config.ts
```

## 本地运行

依赖需要在本目录单独安装：

```powershell
cd web/figma-make
npm install
npm run dev
```

生产构建：

```powershell
npm run build
```

主应用已经在 `web/` 根目录维护自己的依赖。不要因为运行本参考工程，
把 Radix、Tailwind 或 Vite 依赖安装到主应用中。

## 与主应用的关系

- 主应用：`web/src/`，使用 Mantine UI 和 Create React App。
- 参考工程：`web/figma-make/`，使用 Tailwind、Radix 和 Vite。
- 主应用借鉴本工程的视觉语言，但不直接 import 本目录组件。
- 需要迁移设计时，应在 Mantine 组件和 `web/src/styles.css` 中重新实现，
  避免形成两套运行时和样式管线。

## 设计参考要点

- 黑红主色与低饱和旧纸色文字
- 装饰性衬线标题和高字距导航
- 大幅主视觉、剧本封面与分层卡片
- 细边框、暗部渐变和克制的强调色
- 桌面与移动端响应式布局

## 当前状态

- [x] Figma Make 导出源码已保留
- [x] 中文文本按 UTF-8 保存
- [x] 与主应用源码目录隔离
- [x] 授权来源记录在 `ATTRIBUTIONS.md`
- [ ] 本地依赖尚需按需安装
- [ ] 参考工程与主应用不做功能同步保证
