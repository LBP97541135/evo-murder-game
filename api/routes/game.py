"""
EvoMap Murder Game - Game Session Routes

游戏 Session 创建、广播、复盘。
"""

from fastapi import APIRouter, HTTPException

from api.schemas.invoke_types import GameSessionRequest, GameSessionResponse
from api.agents.agent_orchestrator import AgentRole
from api.main import orchestrator

router = APIRouter()


@router.post("/create-session", response_model=GameSessionResponse)
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


@router.post("/broadcast/{session_id}")
async def broadcast_message(session_id: str, msg_type: str, payload: dict, from_role: str):
    """在游戏 Session 中广播消息。"""
    role = AgentRole(from_role)
    return orchestrator.broadcast_message(session_id, msg_type, payload, role)


@router.post("/reflect/{session_id}")
async def post_game_reflection(session_id: str, game_result: dict):
    """游戏结束后，所有 Agent 执行自评并记录经验。"""
    return orchestrator.post_game_reflection(session_id, game_result)
