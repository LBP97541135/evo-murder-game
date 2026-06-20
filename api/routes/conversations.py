"""
EvoMap Murder Game - Conversation Routes

对话记录的保存和查询。每轮 AI 调用的完整三层管道结果持久化。
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from api.db.models import get_session, ConversationTurn

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================
# 请求模型
# ============================

class ConversationSaveRequest(BaseModel):
    session_id: str
    actor_name: str
    chat_messages: list = []
    original_response: str = ""
    critique_response: str = ""
    refined_response: str = ""
    final_response: str = ""


# ============================
# API 端点
# ============================

@router.post("/save")
async def save_conversation(req: ConversationSaveRequest):
    """保存一轮对话记录，同时写入 Agent 游戏状态的 chat_history。"""
    db_session = get_session()
    try:
        turn = ConversationTurn(
            id=f"turn_{uuid.uuid4().hex[:8]}",
            session_id=req.session_id,
            actor_name=req.actor_name,
            chat_messages=req.chat_messages,
            original_response=req.original_response,
            critique_response=req.critique_response,
            refined_response=req.refined_response,
            final_response=req.final_response,
        )
        db_session.add(turn)
        db_session.commit()

        # 同步到 Agent 游戏状态
        try:
            from api.agents.game_engine import game_engine
            from api.agents.game_context import find_agent_key
            if req.final_response and req.actor_name:
                _game = game_engine.get_game(req.session_id)
                _agent_key = find_agent_key(_game, req.actor_name) if _game else None

                if _agent_key:
                    game_engine.add_chat_to_agent(
                        game_id=req.session_id,
                        agent_key=_agent_key,
                        role=req.actor_name,
                        content=req.final_response,
                    )
                elif _game:
                    for key in _game.get("agents", {}):
                        if "dm" in key.lower():
                            continue
                        game_engine.add_chat_to_agent(
                            game_id=req.session_id,
                            agent_key=key,
                            role=req.actor_name,
                            content=req.final_response,
                        )

                game_engine.record_chat(game_id=req.session_id)
        except Exception as sync_err:
            logger.warning(f"同步到 Agent 游戏状态失败（可能游戏不存在）: {sync_err}")

        return {
            "success": True,
            "turn_id": turn.id,
            "message": "对话记录保存成功",
        }
    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=500, detail=f"保存对话记录失败: {str(e)}")
    finally:
        db_session.close()


@router.get("/session/{session_id}")
async def get_conversations(
    session_id: str,
    actor_name: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
):
    """获取指定游戏会话的对话记录。"""
    db_session = get_session()
    try:
        query = db_session.query(ConversationTurn).filter(
            ConversationTurn.session_id == session_id
        )

        if actor_name:
            query = query.filter(ConversationTurn.actor_name == actor_name)

        turns = query.order_by(ConversationTurn.created_at.asc()).limit(limit).all()

        result = []
        for t in turns:
            result.append({
                "id": t.id,
                "sessionId": t.session_id,
                "actorName": t.actor_name,
                "chatMessages": t.chat_messages or [],
                "originalResponse": t.original_response,
                "critiqueResponse": t.critique_response,
                "refinedResponse": t.refined_response,
                "finalResponse": t.final_response,
                "createdAt": t.created_at.isoformat() if t.created_at else "",
            })

        return {
            "success": True,
            "conversations": result,
            "count": len(result),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对话记录失败: {str(e)}")
    finally:
        db_session.close()


@router.delete("/session/{session_id}")
async def clear_conversations(session_id: str):
    """清除指定游戏会话的所有对话记录。"""
    db_session = get_session()
    try:
        deleted = db_session.query(ConversationTurn).filter(
            ConversationTurn.session_id == session_id
        ).delete()
        db_session.commit()

        return {
            "success": True,
            "deleted_count": deleted,
            "message": f"已清除 {deleted} 条对话记录",
        }
    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=500, detail=f"清除对话记录失败: {str(e)}")
    finally:
        db_session.close()
