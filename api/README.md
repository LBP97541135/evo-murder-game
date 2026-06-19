# api/ · README

## 职责
后端 API 服务，基于 Python FastAPI。
负责所有后端逻辑：Agent 管理、EvoMap 通信、LLM 推理、游戏 Session、数据持久化、剧本管理、证物系统、剧透故事。

## 目录结构

```
api/
├── main.py                 ← FastAPI 入口，app初始化 + 路由挂载
├── requirements.txt        ← Python 依赖清单
├── __init__.py             ← 包标记
│
├── config/                 ← 配置管理
│   ├── settings.py         ← .env读取，所有配置变量
│   ├── .env.example        ← 环境变量模板
│   └── README.md
│
├── evomap/                 ← EvoMap A2A Protocol 客户端
│   ├── evomap_client.py    ← 全端点封装（30+方法）
│   ├── __init__.py
│   └── README.md
│
├── agents/                 ← 多Agent编排系统
│   ├── agent_orchestrator.py ← AgentNode + Orchestrator + 角色模板
│   ├── __init__.py
│   └── README.md
│
├── llm/                    ← LLM 推理服务
│   ├── llm_service.py      ← 三层管道 + 5个Provider + 角色Prompt
│   ├── __init__.py
│   └── README.md
│
├── schemas/                ← Pydantic 数据模型
│   ├── invoke_types.py     ← 所有请求/响应模型 + SafeActor
│   ├── __init__.py
│   └── README.md
│
├── db/                     ← 数据持久化
│   ├── models.py           ← SQLAlchemy ORM 模型（15个表 + 转换函数）
│   ├── database.py         ← 连接引擎 + 初始化 + Session
│   ├── __init__.py
│   └── README.md
│
├── routes/                 ← FastAPI 路由定义
│   ├── health.py           ← /health 健康检查
│   ├── agents.py           ← /agents 注册/列表/心跳/进化
│   ├── invoke.py           ← /invoke AI三层管道
│   ├── game.py             ← /game Session/广播/复盘
│   ├── memory.py           ← /memory 记录/召回/状态
│   ├── scripts.py          ← /scripts 剧本CRUD（保存/列表/详情/删除）
│   ├── evidence.py         ← /evidence 证物系统（创建/查询/出示/组合/进度）
│   ├── spoiler_stories.py  ← /spoiler-stories 剧透故事管理
│   ├── __init__.py
│   └── README.md
│
└── README.md               ← 本文件
```

## 当前需求
- [ ] 实际测试所有 EvoMap 端点调用
- [ ] 实际测试三层 LLM 管道
- [ ] 实现流式 SSE 输出
- [ ] 实现 constitution 自动改写逻辑
- [ ] 添加图像生成路由（头像/封面/背景）
- [ ] 添加 Council 治理路由
- [ ] 证据 LLM 反应对接（/evidence/present 接入 llm_service）

## 进度
- ✅ 项目结构从扁平 → 模块化拆分完成
- ✅ 所有 import 路径更新完毕
- ✅ main.py 只做初始化 + 路由挂载
- ✅ routes 从 main.py 单体拆分为 8 个独立文件
- ✅ 数据库从 6 个表扩展到 15 个表（含游戏引擎完整的证物系统/进度表）
- ✅ 剧本 CRUD API（保存/列表/详情/删除，含角色/证物/封面处理）
- ✅ 运行时证物系统（创建/查询/更新/出示/组合/进度追踪，9个端点）
- ✅ 剧透故事管理（CRUD + 批量删除，6个端点）
- ✅ 全部新增端点集成测试通过

## 疑问
- 每个子目录的 README 中已列出各自的具体疑问
- 最关键的阻塞点：EvoMap hello 端点的实际返回格式需要验证
- 证据 /present 的 AI 反应：是在后端内调用 LLM，还是让前端用 /invoke 自己触发？