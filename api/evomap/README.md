# api/evomap/ · README

## 职责
EvoMap GEP-A2A 协议客户端——封装所有与 EvoMap Hub 的交互。
每个 Agent 注册后会获得专属的 EvoMapClient 实例（带自己的 node_id 和 node_secret）。

## 文件清单
| 文件 | 说明 |
|------|------|
| `evomap_client.py` | A2A Protocol 全端点封装（30+ 方法） |
| `__init__.py` | 模块导出 |

## 端点覆盖
| 域 | 方法 | 说明 |
|----|------|------|
| **节点生命周期** | `hello()`, `heartbeat()` | 注册/保活 |
| **Session协作** | `create_session()`, `join_session()`, `send_message()`, `submit_task_result()` | 会话通信 |
| **资产发布** | `publish()`, `validate()`, `fetch()`, `search_assets()` | Gene/Capsule管理 |
| **进化记忆** | `memory_record()`, `memory_recall()`, `memory_status()` | 经验记录/召回 |
| **Council治理** | `council_propose()`, `dialog()` | 五阶段审议 |
| **任务悬赏** | `propose_decomposition()`, `claim_task()`, `complete_task()`, `ask()` | 蜂群/悬赏 |
| **流程编排** | `create_recipe()`, `express_recipe()`, `express_gene()` | Recipe/Organism |
| **积分经济** | `credit_estimate()`, `earnings()` | 积分管理 |
| **发现帮助** | `discover()`, `help()` | 协作发现/文档 |

## 当前需求
- [ ] 实际测试所有端点（Windows curl 有 SSL 问题，必须用 Python httpx）
- [ ] 验证 hello 端点的返回格式是否和文档一致
- [ ] 处理 A2A 信封中 payload 字段的位置（有些端点 payload 在信封内，有些在信封外）
- [ ] 添加 SSE 流式响应支持（当前所有调用都是同步阻塞）
- [ ] 添加重试机制（网络不稳定时自动重试）

## 进度
- ✅ 全端点方法签名完成
- ✅ GEP-A2A 协议信封构建逻辑
- ✅ httpx 客户端（替代有 SSL 问题的 curl）
- ✅ 全局单例 evomap_client（非特定 Agent 的通用调用）

## 疑问
- Session 端点的请求格式——有些直接传 body 不需要信封？需实测确认
- fetch 端点的 search_only 模式是否真的免费？文档说免费但需验证
- heartbeat 是否需要信封？文档示例有的带信封有的不带
