# API 接口文档

> 版本：2.0.0  
> 最后更新：2026-06-25

## 目录

- [概述](#概述)
- [统一响应格式](#统一响应格式)
- [错误码说明](#错误码说明)
- [接口列表](#接口列表)
  - [健康检查](#健康检查)
  - [剧本管理](#剧本管理)
  - [游戏会话](#游戏会话)
  - [选角管理](#选角管理)
  - [阶段推进](#阶段推进)
  - [对话系统](#对话系统)
  - [证物系统](#证物系统)
  - [复盘报告](#复盘报告)
  - [Skill 管理](#skill-管理)
  - [Agent 管理](#agent-管理)
  - [用户管理](#用户管理)

---

## 概述

本项目提供 RESTful API，基于 FastAPI 框架开发。所有接口均返回 JSON 格式数据。

**Base URL**: `http://localhost:8000`

**认证方式**: 当前版本暂不需要认证

---

## 统一响应格式

### 成功响应

```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功"
}
```

### 错误响应

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  }
}
```

---

## 错误码说明

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|-------------|
| `NOT_FOUND` | 资源不存在 | 404 |
| `CREATE_FAILED` | 创建资源失败 | 400 |
| `UPDATE_FAILED` | 更新资源失败 | 400 |
| `DELETE_FAILED` | 删除资源失败 | 400 |
| `FETCH_FAILED` | 获取资源失败 | 400 |
| `MISSING_PARAM` | 缺少必要参数 | 400 |
| `CAST_FAILED` | 选角失败 | 400 |
| `ADVANCE_FAILED` | 阶段推进失败 | 400 |
| `FORCE_FAILED` | 强制跳转失败 | 400 |
| `SEND_FAILED` | 发送消息失败 | 400 |
| `DISCOVER_FAILED` | 发现证物失败 | 400 |
| `PRESENT_FAILED` | 出示证物失败 | 400 |
| `RUN_FAILED` | 运行复盘失败 | 400 |
| `SEARCH_FAILED` | 搜索失败 | 400 |
| `IMPORT_FAILED` | 导入失败 | 400 |
| `EXPORT_FAILED` | 导出失败 | 400 |
| `REVIEW_FAILED` | 审核失败 | 400 |

---

## 接口列表

### 健康检查

#### GET /health

健康检查接口，用于监控服务状态。

**请求示例**:

```bash
curl -X GET http://localhost:8000/health
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "status": "ok",
    "version": "2.0.0"
  },
  "message": ""
}
```

---

### 剧本管理

#### GET /scripts

获取剧本列表。

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | 否 | 剧本状态，默认 "active" |

**请求示例**:

```bash
curl -X GET "http://localhost:8000/scripts/?status=active"
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "scripts": [
      {
        "id": "script_001",
        "title": "古宅惊魂",
        "description": "一座古宅中发生的离奇命案...",
        "author": "张三",
        "version": "1.0.0",
        "genre": "恐怖",
        "difficulty": "medium",
        "duration_minutes": 120,
        "player_count": 6
      }
    ]
  },
  "message": ""
}
```

#### GET /scripts/{script_id}

获取剧本详情。

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| script_id | string | 剧本 ID |

**请求示例**:

```bash
curl -X GET http://localhost:8000/scripts/script_001
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "script": {
      "id": "script_001",
      "title": "古宅惊魂",
      "description": "一座古宅中发生的离奇命案..."
    },
    "characters": [
      {
        "id": "char_001",
        "name": "管家",
        "description": "忠诚的管家..."
      }
    ],
    "truth": {
      "summary": "真相是...",
      "timeline": [...]
    }
  },
  "message": ""
}
```

**错误响应** (404):

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "剧本不存在",
    "details": {}
  }
}
```

#### POST /scripts/import

导入剧本。

**请求体**:

```json
{
  "title": "新剧本",
  "description": "剧本描述",
  "author": "作者",
  "version": "1.0.0",
  "genre": "推理",
  "difficulty": "hard",
  "duration_minutes": 180,
  "player_count": 8
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": "script_new_001",
    "title": "新剧本",
    ...
  },
  "message": ""
}
```

---

### 游戏会话

#### POST /sessions

创建游戏会话。

**请求体**:

```json
{
  "script_id": "script_001",
  "host_user_id": "user_001",
  "title": "周六晚场",
  "player_character_id": "char_001",
  "dm_agent_id": "agent_dm_001"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": "session_abc123",
    "script_id": "script_001",
    "host_user_id": "user_001",
    "title": "周六晚场",
    "current_phase": "setup",
    "status": "active",
    "player_character_id": "char_001",
    "dm_agent_id": "agent_dm_001",
    "created_at": "2026-06-25T10:00:00"
  },
  "message": ""
}
```

#### GET /sessions/{session_id}

获取会话详情。

**请求示例**:

```bash
curl -X GET http://localhost:8000/sessions/session_abc123
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": "session_abc123",
    "script_id": "script_001",
    "current_phase": "investigation",
    "status": "active",
    ...
  },
  "message": ""
}
```

#### GET /sessions/{session_id}/snapshot

获取游戏快照（会话 + 阶段事件 + 角色分配）。

**请求示例**:

```bash
curl -X GET http://localhost:8000/sessions/session_abc123/snapshot
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "session": {
      "id": "session_abc123",
      "current_phase": "investigation",
      "status": "active"
    },
    "phase_events": [
      {
        "id": "phase_001",
        "from_phase": "setup",
        "to_phase": "intro",
        "reason": "auto_advance",
        "triggered_by": "system"
      }
    ],
    "casts": [
      {
        "id": "cast_001",
        "character_id": "char_001",
        "actor_type": "human",
        "actor_id": "user_001",
        "role_name": "管家"
      }
    ]
  },
  "message": ""
}
```

#### POST /sessions/{session_id}/end

结束游戏会话。

**请求示例**:

```bash
curl -X POST http://localhost:8000/sessions/session_abc123/end
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "message": "游戏已结束",
    "session_id": "session_abc123"
  },
  "message": ""
}
```

---

### 选角管理

#### POST /sessions/{session_id}/cast

设置选角（批量分配角色）。

**请求体**:

```json
[
  {
    "character_id": "char_001",
    "actor_type": "human",
    "actor_id": "user_001",
    "user_id": "user_001",
    "role_name": "管家",
    "is_player": true
  },
  {
    "character_id": "char_002",
    "actor_type": "agent",
    "actor_id": "agent_001",
    "agent_id": "agent_001",
    "role_name": "厨师",
    "is_player": false
  }
]
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "session_id": "session_abc123",
    "casts": [
      {
        "id": "cast_001",
        "character_id": "char_001",
        "actor_type": "human",
        "role_name": "管家"
      },
      {
        "id": "cast_002",
        "character_id": "char_002",
        "actor_type": "agent",
        "role_name": "厨师"
      }
    ]
  },
  "message": ""
}
```

#### GET /sessions/{session_id}/cast

获取选角信息。

**请求示例**:

```bash
curl -X GET http://localhost:8000/sessions/session_abc123/cast
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "session_id": "session_abc123",
    "casts": [
      {
        "id": "cast_001",
        "character_id": "char_001",
        "actor_type": "human",
        "actor_id": "user_001",
        "role_name": "管家"
      }
    ]
  },
  "message": ""
}
```

#### DELETE /sessions/{session_id}/cast

重置选角（删除所有角色分配）。

**请求示例**:

```bash
curl -X DELETE http://localhost:8000/sessions/session_abc123/cast
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "message": "选角已重置"
  },
  "message": ""
}
```

---

### 阶段推进

#### GET /sessions/{session_id}/phase

获取当前阶段。

**请求示例**:

```bash
curl -X GET http://localhost:8000/sessions/session_abc123/phase
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "session_id": "session_abc123",
    "phase": "investigation"
  },
  "message": ""
}
```

**阶段枚举值**:

- `setup` - 准备阶段
- `intro` - 介绍阶段
- `script_reading` - 剧本阅读
- `investigation` - 调查阶段
- `deduction` - 推理阶段
- `voting` - 投票阶段
- `reveal` - 揭晓阶段
- `review` - 复盘阶段

#### POST /sessions/{session_id}/phase/advance

推进到下一阶段。

**请求示例**:

```bash
curl -X POST http://localhost:8000/sessions/session_abc123/phase/advance
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "session_id": "session_abc123",
    "from_phase": "setup",
    "to_phase": "intro",
    "event_id": "phase_001"
  },
  "message": ""
}
```

**错误响应** (400):

```json
{
  "success": false,
  "error": {
    "code": "ADVANCE_FAILED",
    "message": "已经是最终阶段，无法继续推进",
    "details": {}
  }
}
```

#### POST /sessions/{session_id}/phase/force

强制跳转到指定阶段（管理员权限）。

**请求体**:

```json
{
  "target_phase": "voting",
  "reason": "admin_force"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "session_id": "session_abc123",
    "from_phase": "investigation",
    "to_phase": "voting",
    "reason": "admin_force",
    "event_id": "phase_002"
  },
  "message": ""
}
```

---

### 对话系统

#### GET /sessions/{session_id}/messages

获取消息列表。

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| thread_id | string | 否 | 对话线程 ID |
| limit | int | 否 | 返回数量上限，默认 50 |

**请求示例**:

```bash
curl -X GET "http://localhost:8000/sessions/session_abc123/messages/?thread_id=thread_001&limit=20"
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "session_id": "session_abc123",
    "messages": [
      {
        "id": "msg_001",
        "thread_id": "thread_001",
        "sender_type": "human",
        "sender_id": "user_001",
        "sender_name": "玩家",
        "content": "我发现了一个线索！",
        "created_at": "2026-06-25T10:30:00"
      }
    ]
  },
  "message": ""
}
```

#### POST /sessions/{session_id}/messages

发送消息。

**请求体**:

```json
{
  "thread_id": "thread_001",
  "sender_type": "human",
  "sender_id": "user_001",
  "sender_name": "玩家",
  "content": "我认为管家是凶手！"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": "msg_002",
    "thread_id": "thread_001",
    "sender_type": "human",
    "sender_id": "user_001",
    "sender_name": "玩家",
    "content": "我认为管家是凶手！",
    "created_at": "2026-06-25T10:35:00"
  },
  "message": ""
}
```

**错误响应** (400):

```json
{
  "success": false,
  "error": {
    "code": "MISSING_PARAM",
    "message": "缺少 thread_id 或 content 参数",
    "details": {}
  }
}
```

#### GET /sessions/{session_id}/messages/threads

获取对话线程列表。

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| thread_type | string | 否 | 线程类型（public/private/dm/system） |

**请求示例**:

```bash
curl -X GET "http://localhost:8000/sessions/session_abc123/messages/threads?thread_type=public"
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "session_id": "session_abc123",
    "threads": [
      {
        "id": "thread_001",
        "thread_type": "public",
        "title": "公共讨论",
        "status": "active",
        "participant_ids": ["user_001", "agent_001"]
      }
    ]
  },
  "message": ""
}
```

#### POST /sessions/{session_id}/messages/threads

创建对话线程。

**请求体**:

```json
{
  "thread_type": "public",
  "participant_ids": ["user_001", "agent_001", "agent_002"]
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": "thread_002",
    "session_id": "session_abc123",
    "thread_type": "public",
    "status": "active",
    "participant_ids": ["user_001", "agent_001", "agent_002"],
    "created_at": "2026-06-25T10:40:00"
  },
  "message": ""
}
```

---

### 证物系统

#### GET /sessions/{session_id}/evidences

获取证物列表。

**请求示例**:

```bash
curl -X GET http://localhost:8000/sessions/session_abc123/evidences
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "session_id": "session_abc123",
    "evidences": [
      {
        "id": "ev_001",
        "name": "血迹",
        "category": "physical",
        "importance": "high",
        "basic_description": "地板上的血迹",
        "discovery_state": "discovered",
        "visibility": "public",
        "is_public": true
      }
    ]
  },
  "message": ""
}
```

#### GET /sessions/{session_id}/evidences/public

获取公开证物。

**请求示例**:

```bash
curl -X GET http://localhost:8000/sessions/session_abc123/evidences/public
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "session_id": "session_abc123",
    "public_evidences": [
      {
        "id": "ev_001",
        "name": "血迹",
        "is_public": true
      }
    ]
  },
  "message": ""
}
```

#### POST /sessions/{session_id}/evidences/discover

发现证物。

**请求体**:

```json
{
  "evidence_id": "ev_001"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": "ev_001",
    "name": "血迹",
    "discovery_state": "discovered",
    "updated_at": "2026-06-25T11:00:00"
  },
  "message": ""
}
```

**错误响应** (400):

```json
{
  "success": false,
  "error": {
    "code": "DISCOVER_FAILED",
    "message": "证物 ev_001 不属于会话 session_abc123",
    "details": {}
  }
}
```

#### POST /sessions/{session_id}/evidences/present

出示证物。

**请求体**:

```json
{
  "evidence_id": "ev_001",
  "presented_to": "char_002",
  "is_public": false
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": "ev_001",
    "name": "血迹",
    "visibility": "presented",
    "metadata_json": {
      "presentations": [
        {
          "presented_to": "char_002",
          "is_public": false,
          "presented_at": "2026-06-25T11:05:00"
        }
      ]
    }
  },
  "message": ""
}
```

---

### 复盘报告

#### GET /sessions/{session_id}/review

获取复盘报告。

**请求示例**:

```bash
curl -X GET http://localhost:8000/sessions/session_abc123/review
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "session_id": "session_abc123",
    "review": {
      "id": "review_001",
      "session_id": "session_abc123",
      "status": "completed",
      "truth_summary": "真相是...",
      "player_result_json": {...},
      "key_clues_json": [...],
      "timeline_json": [...]
    }
  },
  "message": ""
}
```

**无复盘时的响应**:

```json
{
  "success": true,
  "data": {
    "session_id": "session_abc123",
    "review": null
  },
  "message": ""
}
```

#### POST /sessions/{session_id}/review/run

运行复盘（触发生成复盘报告）。

**请求示例**:

```bash
curl -X POST http://localhost:8000/sessions/session_abc123/review/run
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "review_id": "review_001",
    "session_id": "session_abc123",
    "status": "generating"
  },
  "message": ""
}
```

---

### Skill 管理

#### GET /skills

获取 Skill 列表。

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | 否 | Skill 分类 |
| status | string | 否 | Skill 状态 |

**请求示例**:

```bash
curl -X GET "http://localhost:8000/skills/?category=hosting&status=active"
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "skills": [
      {
        "id": "skill_001",
        "name": "DM 控场技巧",
        "category": "hosting",
        "description": "如何控制游戏节奏",
        "status": "active",
        "usage_count": 15,
        "success_count": 12
      }
    ]
  },
  "message": ""
}
```

#### POST /skills

创建 Skill。

**请求体**:

```json
{
  "name": "DM 控场技巧",
  "version": "1.0.0",
  "type": "prompt_skill",
  "category": "hosting",
  "applicable_roles": ["dm"],
  "signals": ["控场", "节奏"],
  "description": "如何控制游戏节奏",
  "prompt_content": "作为 DM，你应该...",
  "strategy": "观察玩家情绪，适时推进",
  "examples": "示例场景...",
  "anti_patterns": "避免长时间沉默",
  "injection_mode": "append_system_prompt",
  "injection_priority": 50,
  "max_tokens": 800
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": "skill_new_001",
    "name": "DM 控场技巧",
    "category": "hosting",
    "status": "active",
    "created_at": "2026-06-25T12:00:00"
  },
  "message": ""
}
```

#### GET /skills/{skill_id}

获取 Skill 详情。

**请求示例**:

```bash
curl -X GET http://localhost:8000/skills/skill_001
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": "skill_001",
    "name": "DM 控场技巧",
    "version": "1.0.0",
    "type": "prompt_skill",
    "category": "hosting",
    "applicable_roles": ["dm"],
    "signals": ["控场", "节奏"],
    "description": "如何控制游戏节奏",
    "prompt_content": "作为 DM，你应该...",
    "status": "active",
    "usage_count": 15,
    "success_count": 12
  },
  "message": ""
}
```

#### PATCH /skills/{skill_id}

更新 Skill。

**请求体** (部分更新):

```json
{
  "name": "新名称",
  "description": "新描述"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": "skill_001",
    "name": "新名称",
    "description": "新描述",
    "updated_at": "2026-06-25T12:30:00"
  },
  "message": ""
}
```

#### DELETE /skills/{skill_id}

删除 Skill。

**请求示例**:

```bash
curl -X DELETE http://localhost:8000/skills/skill_001
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "message": "Skill 已删除"
  },
  "message": ""
}
```

#### POST /skills/search

搜索 Skill。

**请求体**:

```json
{
  "role": "dm",
  "category": "hosting",
  "signals": ["控场"],
  "limit": 10
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "skills": [
      {
        "id": "skill_001",
        "name": "DM 控场技巧",
        "category": "hosting"
      }
    ]
  },
  "message": ""
}
```

#### POST /skills/import

导入 Skill。

**请求体**:

```json
{
  "name": "导入的 Skill",
  "category": "hosting",
  "prompt_content": "内容...",
  "version": "1.0.0"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": "skill_imported_001",
    "name": "导入的 Skill",
    "status": "active"
  },
  "message": ""
}
```

#### GET /skills/{skill_id}/export

导出 Skill。

**请求示例**:

```bash
curl -X GET http://localhost:8000/skills/skill_001/export
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": "skill_001",
    "name": "DM 控场技巧",
    "version": "1.0.0",
    "type": "prompt_skill",
    "category": "hosting",
    "applicable_roles": ["dm"],
    "signals": ["控场"],
    "description": "如何控制游戏节奏",
    "prompt_content": "作为 DM，你应该...",
    "metadata": {...}
  },
  "message": ""
}
```

#### POST /skills/{skill_id}/review

审核 Skill。

**请求体**:

```json
{
  "status": "approved",
  "reviewed_by": "admin_001",
  "comment": "质量良好，通过审核"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": "skill_001",
    "review_status": "approved",
    "reviewed_by": "admin_001",
    "review_comment": "质量良好，通过审核"
  },
  "message": ""
}
```

---

### Agent 管理

#### GET /agents

获取 Agent 列表。

**请求示例**:

```bash
curl -X GET http://localhost:8000/agents
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "agents": [
      {
        "id": "agent_001",
        "name": "DM Agent",
        "role": "dm",
        "model": "gpt-4",
        "status": "active",
        "domains": ["hosting", "narrative-control"]
      }
    ]
  },
  "message": ""
}
```

#### POST /agents

创建 Agent。

**请求体**:

```json
{
  "name": "DM Agent",
  "role": "dm",
  "model": "gpt-4",
  "persona_id": "persona_001",
  "status": "active",
  "domains": ["hosting", "narrative-control"],
  "identity_doc": "你是一个专业的主持人...",
  "constitution": "绝不泄露答案..."
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": "agent_new_001",
    "name": "DM Agent",
    "role": "dm",
    "status": "active",
    "created_at": "2026-06-25T13:00:00"
  },
  "message": ""
}
```

#### GET /agents/{agent_id}

获取 Agent 详情。

**请求示例**:

```bash
curl -X GET http://localhost:8000/agents/agent_001
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": "agent_001",
    "name": "DM Agent",
    "role": "dm",
    "model": "gpt-4",
    "identity_doc": "你是一个专业的主持人...",
    "constitution": "绝不泄露答案...",
    "status": "active"
  },
  "message": ""
}
```

#### GET /agents/{agent_id}/state

获取 Agent 运行时状态。

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| session_id | string | 是 | 游戏会话 ID |

**请求示例**:

```bash
curl -X GET "http://localhost:8000/agents/agent_001/state?session_id=session_abc123"
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "agent_id": "agent_001",
    "state": {
      "current_phase": "investigation",
      "memory_count": 5,
      "last_action": "broadcast_message"
    }
  },
  "message": ""
}
```

---

### 用户管理

#### GET /users/profile

获取用户信息。

**查询参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| user_id | string | 否 | 用户 ID，默认 "default" |

**请求示例**:

```bash
curl -X GET "http://localhost:8000/users/profile?user_id=user_001"
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "user_id": "user_001",
    "display_name": "玩家",
    "level": 1,
    "preferred_genres": [],
    "preferred_difficulty": "medium",
    "total_games": 0
  },
  "message": ""
}
```

#### PATCH /users/profile

更新用户信息。

**请求体**:

```json
{
  "display_name": "新昵称",
  "preferred_genres": ["推理", "恐怖"],
  "preferred_difficulty": "hard"
}
```

**响应示例**:

```json
{
  "success": true,
  "data": {
    "message": "用户信息已更新",
    "user_id": "user_001"
  },
  "message": ""
}
```

---

## 附录

### 游戏阶段流转

```
setup → intro → script_reading → investigation → deduction → voting → reveal → review
准备    介绍    剧本阅读          调查阶段        推理阶段    投票    揭晓    复盘
```

### 数据类型说明

- **session_id**: 游戏会话 ID，格式 `session_xxxxxxxx`
- **script_id**: 剧本 ID，格式 `script_xxxxxxxx`
- **character_id**: 角色 ID，格式 `char_xxxxxxxx`
- **agent_id**: Agent ID，格式 `agent_xxxxxxxx`
- **skill_id**: Skill ID，格式 `skill_xxxxxxxx`
- **evidence_id**: 证物 ID，格式 `ev_xxxxxxxx`
- **thread_id**: 对话线程 ID，格式 `thread_xxxxxxxx`
- **message_id**: 消息 ID，格式 `msg_xxxxxxxx`

### 线程类型

- `public`: 公共讨论
- `private`: 私聊
- `dm`: DM 专属
- `system`: 系统消息

### 发送者类型

- `human`: 人类玩家
- `agent`: AI Agent
- `dm`: 主持人
- `system`: 系统

---

**文档结束**
