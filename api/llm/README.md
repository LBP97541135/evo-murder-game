# api/llm/ · README

## 职责
LLM 推理服务——三层 AI 管道（respond_initial → critique → refine）和多 Provider 支持。

核心机制：
- **三层管道**：生成 → 批评检查 → 修订，防止 Agent 泄露角色秘密或违规
- **多 Provider**：Anthropic / OpenAI / Groq / OpenRouter / Ollama，通过 EvoMap 中转站统一调用
- **角色 Prompt**：DM/陪玩/助手三种角色的 system prompt 模板

## 文件清单
| 文件 | 说明 |
|------|------|
| `llm_service.py` | 三层管道 + 5个Provider + 角色Prompt + invoke_with_pipeline |
| `evidence_llm_service.py` | 证物出示AI反应生成（prompt构建 + 反应解析 + LLM调用占位） |
| `__init__.py` | 模块导出（含 evidence_llm_service） |

## 三层管道详解

```
respond_initial(system_prompt, user_message, ...)
    → 生成初始回复

critique(initial_response, critique_prompt, ...)
    → 检查回复是否违反指定原则
    → 返回 "NONE" 表示无违规，或指出具体违规

refine(initial_response, critique_result, system_prompt, user_message, ...)
    → 根据批评修订回复

invoke_with_pipeline(...)
    → 一次性执行完整管道
    → 返回 {initial, critique, refined, final}
    → final = refined（如果有违规）或 initial（如果无违规）
```

## Critique 规则（剧本杀场景）

1. 回复不能包含角色秘密的直接泄露
2. 回复不能包含未获得的线索
3. 回复不能包含其他角色的私密信息
4. 回复不能违背角色性格设定

## 当前需求
- [ ] 实际测试三层管道（特别是 critique 能否有效检测剧透）
- [ ] 实现 SSE 流式输出（/invoke/stream）
- [ ] 添加 streaming 版本的 respond_initial（逐 token 输出）
- [ ] 优化 critique prompt（针对不同角色类型定制不同审查规则）
- [ ] 添加 LLM 调用计费追踪（记录每次调用的 token 用量）

## 进度
- ✅ 三层管道核心逻辑完成
- ✅ 5个 Provider 支持（Anthropic/OpenAI/Groq/OpenRouter/Ollama）
- ✅ 角色系统 Prompt 模板（DM/陪玩/助手）
- ✅ check_whether_to_refine 逻辑

## 疑问
- critique 层消耗额外的 token——黑客松积分有限，是否需要 skip_critique 选项？
- EvoMap 中转站的 token 限制是多少？是否和 OpenAI 一样？
- 流式 SSE 的实现——EvoMap 中转站是否支持 streaming？
