"""
EvoMap Murder Game - Game Session Routes

游戏 Session 创建、阶段管理、广播、投票、复盘。
v2.1 新增：Agent 游戏状态、意图系统、记忆压缩。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from api.schemas.invoke_types import GameSessionRequest, GameSessionResponse
from api.agents.agent_orchestrator import AgentRole
from api.agents.game_engine import game_engine, GamePhase
from api.orchestrator import orchestrator

router = APIRouter()


# ============================
# 请求模型
# ============================

class VoteRequest(BaseModel):
    killer: str
    motive: str = ""
    voter: str = "player"


class PhaseForceRequest(BaseModel):
    phase: str


class AgentChatRequest(BaseModel):
    session_id: str
    agent_key: str
    content: str
    role: str = "agent"  # agent / player / dm


class ApproveIntentRequest(BaseModel):
    intent_type: str      # interject / private_chat / present_evidence
    approved: bool


# ============================
# 游戏 Session
# ============================

@router.post("/create-session", response_model=GameSessionResponse)
async def create_game_session(req: GameSessionRequest):
    """创建游戏 Session，同时初始化游戏引擎和所有 Agent 游戏状态。"""
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

    # 初始化游戏引擎（同时初始化 Agent 游戏状态 + 胶囊注入）
    game_engine.create_game(script_id=req.script_id, session_id=session_id)

    return GameSessionResponse(
        session_id=session_id,
        participants=session_info.get("companions", []),
        status="active",
    )


# ============================
# 游戏阶段
# ============================

@router.get("/phase/{session_id}")
async def get_game_phase(session_id: str):
    """获取当前游戏阶段信息。"""
    info = game_engine.get_phase_info(session_id)
    if "error" in info:
        raise HTTPException(status_code=404, detail=info["error"])
    return info


@router.post("/phase/{session_id}/advance")
async def advance_game_phase(session_id: str):
    """推进到下一阶段，同时触发所有 Agent 的记忆压缩。"""
    result = game_engine.advance_phase(session_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


@router.post("/phase/{session_id}/force")
async def force_game_phase(session_id: str, req: PhaseForceRequest):
    """强制跳转到指定阶段（DM权限）。"""
    result = game_engine.force_phase(session_id, req.phase)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


# ============================
# 投票
# ============================

@router.post("/vote/{session_id}")
async def submit_vote(session_id: str, req: VoteRequest):
    """提交推理投票（凶手+动机）。"""
    result = game_engine.submit_vote(
        game_id=session_id,
        killer=req.killer,
        motive=req.motive,
        voter=req.voter,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


# ============================
# 消息广播
# ============================

@router.post("/broadcast/{session_id}")
async def broadcast_message(session_id: str, msg_type: str, payload: dict, from_role: str):
    """在游戏 Session 中广播消息。"""
    try:
        role = AgentRole(from_role)
    except ValueError:
        role = AgentRole.DM
    return orchestrator.broadcast_message(session_id, msg_type, payload, role)


# ============================
# 对话计数
# ============================

@router.post("/chat-count/{session_id}")
async def record_chat(session_id: str):
    """记录一次对话（用于阶段推进条件判断）。"""
    game_engine.record_chat(session_id)
    game = game_engine.get_game(session_id)
    return {
        "success": True,
        "chat_count": game.get("chat_count", 0) if game else 0,
        "can_advance": game_engine.can_advance(session_id),
    }


# ============================
# 复盘反思
# ============================

@router.post("/reflect/{session_id}")
async def post_game_reflection(session_id: str, game_result: dict):
    """游戏结束后，所有 Agent 执行自评并记录经验。"""
    return orchestrator.post_game_reflection(session_id, game_result)


# ============================
# 后剧情模式
# ============================

class PostGameRevealRequest(BaseModel):
    """后剧情请求——投票后的真相交代。"""
    killer: str = ""
    motive: str = ""
    voter: str = "player"
    correct: bool = False
    script_type: str = ""


@router.post("/reveal/{session_id}")
async def post_game_reveal(session_id: str, req: PostGameRevealRequest):
    """投票后执行后剧情——凶手交代 + DM 揭晓真相。

    自动调用 LLM 生成凶手交代和真相总结。
    """
    vote_result = {
        "killer": req.killer,
        "motive": req.motive,
        "voter": req.voter,
        "correct": req.correct,
        "script_type": req.script_type,
    }
    result = orchestrator.post_game_reveal(session_id, vote_result)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result)
    return result


@router.post("/reveal/{session_id}/spoiler")
async def generate_spoiler_story(session_id: str, req: PostGameRevealRequest):
    """投票后生成剧透故事——完整游戏剧情回顾。"""
    vote_result = {
        "killer": req.killer,
        "motive": req.motive,
        "voter": req.voter,
        "correct": req.correct,
    }
    result = orchestrator.generate_spoiler_story(session_id, vote_result)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result)
    return result


# ============================
# Agent 游戏状态
# ============================

@router.get("/agent-state/{session_id}/{agent_key}")
async def get_agent_state(session_id: str, agent_key: str):
    """获取指定 Agent 的完整游戏状态（记忆/角色/意图/证物）。"""
    state = game_engine.get_agent_state(session_id, agent_key)
    if not state:
        raise HTTPException(status_code=404, detail="Agent state not found")
    return {"success": True, "state": state}


# ============================
# Agent 行动意图
# ============================

@router.get("/intents/{session_id}/{agent_key}")
async def get_agent_intents(session_id: str, agent_key: str):
    """获取 Agent 当前的行动意图（已生成或空）。"""
    result = game_engine.get_agent_intents(session_id, agent_key)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result)
    return result


@router.post("/intents/{session_id}/{agent_key}/generate")
async def generate_agent_intents(session_id: str, agent_key: str):
    """让 Agent 根据当前局势生成行动意图（插队/私聊/出示证物）。"""
    result = game_engine.generate_agent_intents(session_id, agent_key)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


@router.post("/intents/{session_id}/{agent_key}/approve")
async def approve_agent_intent(session_id: str, agent_key: str, req: ApproveIntentRequest):
    """玩家批准或拒绝 Agent 的某个行动意图。"""
    result = game_engine.approve_intent(session_id, agent_key, req.intent_type, req.approved)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


# ============================
# Agent 发言
# ============================

@router.post("/agent-chat/{session_id}")
async def agent_chat(session_id: str, req: AgentChatRequest):
    """Agent 发言（带角色+记忆+证物感知，自动写入 chat_history）。"""
    game = game_engine.get_game(session_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # 写入 chat_history
    game_engine.add_chat_to_agent(session_id, req.agent_key, req.role, req.content)
    game_engine.record_chat(session_id, from_agent=req.agent_key, content=req.content)

    return {
        "success": True,
        "session_id": session_id,
        "agent_key": req.agent_key,
        "chat_count": game.get("chat_count", 0),
    }
