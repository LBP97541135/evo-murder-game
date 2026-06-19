"""
EvoMap Murder Game - Game Session Routes

游戏 Session 创建、阶段管理、广播、投票、复盘。
"""

from fastapi import APIRouter, HTTPException

from api.schemas.invoke_types import GameSessionRequest, GameSessionResponse
from api.agents.agent_orchestrator import AgentRole
from api.agents.game_engine import game_engine, GamePhase
from api.orchestrator import orchestrator
from pydantic import BaseModel
from typing import Optional

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


# ============================
# 游戏 Session
# ============================

@router.post("/create-session", response_model=GameSessionResponse)
async def create_game_session(req: GameSessionRequest):
    """创建游戏 Session，同时初始化游戏引擎状态。"""
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

    # 初始化游戏引擎
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
    """推进到下一阶段。"""
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
