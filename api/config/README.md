# api/config/ · README

## 职责
配置管理——从 `.env` 文件读取所有参数，统一对外暴露。
包括：AI 推理配置、EvoMap A2A 配置、数据库配置、图像生成配置、应用配置。

## 文件清单
| 文件 | 说明 |
|------|------|
| `settings.py` | 所有配置变量，从 .env 读取，带默认值 |
| `.env.example` | 环境变量示例模板（⚠️ 真实的 .env 不提交到 git） |

## 当前需求
- [ ] 根据实际 EvoMap API 调用情况微调默认值
- [ ] 补充 EvoMap LLM 中转站的 model 列表（哪些模型可用）
- [ ] 补充 EvoMap 三套认证体系的详细配置项

## 进度
- ✅ 基础配置框架完成（6个配置域：AI推理/EvoMap/数据库/图像/应用/LLM中转）

## 疑问
- EvoMap LLM 中转站实际可用的 model 名称列表是什么？（文档只提到 evomap-gemini-3.1-pro-preview）
- 火山引擎图像生成的 access_key/secret_key 是否还需要？（剧本杀需要头像/封面）
