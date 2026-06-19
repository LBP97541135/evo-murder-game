"""
EvoMap Murder Game - FastAPI Main Entry Point

API 路由、Agent 注册、游戏 Session、AI 调用、进化管理。
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from api.settings import DEBUG
from api.invoke_types import (
    InvocationRequest, InvocationResponse,
    AgentRegistrationRequest, AgentRegistrationResponse,
    GameSessionRequest, GameSessionResponse,
    MemoryRecordRequest, MemoryRecallRequest,
    EvolutionUpdateRequest,
)
from api.llm_service import invoke_with_pipeline, ROLE_SYSTEM_PROMPTS
from api.agent_orchestrator import AgentOrchestrator, AgentNode, AgentRole
from api.models import init_db

logger = logging.getLogger(__name__)

# ============================
# App Init
# ============================
app = FastAPI(
    title="EvoMap Murder Game",
    description="多Agent自进化剧本杀系统 - 基于 EvoMap GEP-A2A 协议",
    version="2.0.0",
    debug=DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
init_db()

# 全局编排器
orchestrator = AgentOrchestrator()

# 静态文件（如有前端 build）
static_dir = Path(__file__).parent.parent / "web" / "build"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ============================
# Health Check
# ============================

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "agents_registered": len(orchestrator.agents),
        "active_sessions": len(orchestrator.sessions),
    }


# ============================
# Agent Management
# ============================

@app.post("/agents/register", response_model=AgentRegistrationResponse)
async def register_agent(req: AgentRegistrationRequest):
    """注册一个新 Agent 到系统（同时注册到 EvoMap 网络）。"""
    role = AgentRole(req.role)
    agent = AgentNode(
        role=role,
        name=req.name,
        model=req.model,
        identity_doc=req.identity_doc,
        constitution=req.constitution,
    )
    key = orchestrator.add_agent(agent)
    result = agent.register()

    if "error" in result:
        raise HTTPException(status_code=500, detail=result)

    return AgentRegistrationResponse(
        node_id=agent.node_id or "",
        node_secret=agent.node_secret or "",
        claim_url=result.get("claim_url", ""),
        claim_code=result.get("claim_code", ""),
        status="alive",
    )


@app.get("/agents/list")
async def list_agents():
    """列出所有已注册的 Agent。"""
    agents = []
    for key, agent in orchestrator.agents.items():
        agents.append({
            "key": key,
            "name": agent.name,
            "role": agent.role.value,
            "node_id": agent.node_id or "",
            "registered": agent.registered,
            "model": agent.model,
        })
    return {"agents": agents}


@app.post("/agents/heartbeat/{agent_key}")
async def agent_heartbeat(agent_key: str):
    """发送心跳保活。"""
    agent = orchestrator.agents.get(agent_key)
    if not agent or not agent.registered:
        raise HTTPException(status_code=404, detail="Agent not found or not registered")
    return agent.heartbeat()


@app.post("/agents/evolve/{agent_key}")
async def evolve_agent(agent_key: str, req: EvolutionUpdateRequest):
    """更新 Agent 的 constitution 或 identity_doc（进化核心操作）。"""
    agent = orchestrator.agents.get(agent_key)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if req.update_type == "constitution":
        agent.update_constitution(req.new_content)
    elif req.update_type == "identity_doc":
        agent.update_identity(req.new_content)
    else:
        raise HTTPException(status_code=400, detail="Invalid update_type")

    return {
        "agent_key": agent_key,
        "update_type": req.update_type,
        "new_content": req.new_content,
        "status": "updated",
    }


# ============================
# AI Invocation
# ============================

@app.post("/invoke", response_model=InvocationResponse)
async def invoke_ai(req: InvocationRequest):
    """调用 AI 生成回复（三层管道：initial → critique → refine）。"""
    role = req.actor.role_type or "companion"
    system_prompt = ROLE_SYSTEM_PROMPTS.get(role, ROLE_SYSTEM_PROMPTS["companion"])

    # 将角色信息融入 system prompt
    system_prompt += f"\n\n当前角色：{req.actor.name}\n角色简介：{req.actor.bio}\n性格：{req.actor.personality}"

    if req.actor.secret:
        system_prompt += f"\n角色秘密（仅你自己知道）：{req.actor.secret}"

    # 构建用户消息
    user_message = ""
    for msg in req.chat_messages:
        user_message += f"{msg.role}: {msg.content}\n"

    # Critique 规则——防止剧透和违规
    critique_prompt = (
        "1. 回复不能包含角色秘密的直接泄露\n"
        "2. 回复不能包含未获得的线索\n"
        "3. 回复不能包含其他角色的私密信息\n"
        "4. 回复不能违背角色性格设定"
    )

    result = invoke_with_pipeline(
        system_prompt=system_prompt,
        user_message=user_message,
        critique_prompt=critique_prompt,
        skip_critique=False,
    )

    return InvocationResponse(
        original=result["initial"],
        critique=result.get("critique", ""),
        refined=result.get("refined", ""),
        final_response=result["final"],
    )


# ============================
# Game Session
# ============================

@app.post("/game/create-session", response_model=GameSessionResponse)
async def create_game_session(req: GameSessionRequest):
    """创建游戏 Session。"""
    if not orchestrator.agents:
        raise HTTPException(status_code=400, detail="No agents registered yet")

    result = orchestrator.create_game_session(
        topic=req.topic,
        script_name=req.script_id,
    )

    if "error" in result:
        raise HTTPException(status_code=500, detail=result)

    session_id = result.get("session_id", "")
    session_info = orchestrator.sessions.get(session_id, {})

    return GameSessionResponse(
        session_id=session_id,
        participants=session_info.get("companions", []),
        status="active",
    )


@app.post("/game/broadcast/{session_id}")
async def broadcast_message(session_id: str, msg_type: str, payload: dict, from_role: str):
    """在游戏 Session 中广播消息。"""
    role = AgentRole(from_role)
    return orchestrator.broadcast_message(session_id, msg_type, payload, role)


@app.post("/game/reflect/{session_id}")
async def post_game_reflection(session_id: str, game_result: dict):
    """游戏结束后，所有 Agent 执行自评并记录经验。"""
    return orchestrator.post_game_reflection(session_id, game_result)


# ============================
# Memory & Evolution
# ============================

@app.post("/memory/record")
async def record_memory(req: MemoryRecordRequest):
    """记录 Agent 经验到 EvoMap 私有记忆库。"""
    agent = None
    for a in orchestrator.agents.values():
        if a.node_id == req.node_id:
            agent = a
            break
    if not agent or not agent.registered:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent.record_experience(
        signals=req.signals, gene_id=req.gene_id,
        status=req.status, score=req.score, summary=req.summary,
    )


@app.post("/memory/recall")
async def recall_memory(req: MemoryRecallRequest):
    """召回 Agent 历史经验。"""
    agent = None
    for a in orchestrator.agents.values():
        if a.node_id == req.node_id:
            agent = a
            break
    if not agent or not agent.registered:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent.recall_experience(signals=req.signals, limit=req.limit)


@app.get("/memory/status/{agent_key}")
async def memory_status(agent_key: str):
    """查看 Agent 记忆概况。"""
    agent = orchestrator.agents.get(agent_key)
    if not agent or not agent.registered:
        raise HTTPException(status_code=404, detail="Agent not found or not registered")
    return agent.client.memory_status()
