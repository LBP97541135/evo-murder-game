# -*- coding: utf-8 -*-
"""对话消息路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.db.base import get_db
from api.core.responses import success_response, error_response
from api.services.conversation_service import ConversationService

router = APIRouter(prefix="/sessions/{session_id}/messages", tags=["对话"])


@router.get("/")
def get_messages(session_id: str, thread_id: str = None, limit: int = 50, db: Session = Depends(get_db)):
    """获取消息列表"""
    try:
        service = ConversationService(db)
        messages = service.get_messages(session_id, thread_id=thread_id, limit=limit)
        return success_response({"session_id": session_id, "messages": messages})
    except Exception as e:
        return error_response(code="FETCH_FAILED", message=str(e))


@router.post("/")
def send_message(session_id: str, data: dict, db: Session = Depends(get_db)):
    """发送消息"""
    try:
        service = ConversationService(db)
        thread_id = data.get("thread_id")
        sender_type = data.get("sender_type", "human")
        sender_id = data.get("sender_id", "")
        sender_name = data.get("sender_name", "")
        content = data.get("content", "")
        if not thread_id or not content:
            return error_response(code="MISSING_PARAM", message="缺少 thread_id 或 content 参数")
        message = service.send_message(
            session_id=session_id,
            thread_id=thread_id,
            sender_type=sender_type,
            sender_id=sender_id,
            sender_name=sender_name,
            content=content,
        )
        return success_response(message)
    except Exception as e:
        return error_response(code="SEND_FAILED", message=str(e))


@router.get("/threads")
def get_threads(session_id: str, thread_type: str = None, db: Session = Depends(get_db)):
    """获取对话线程列表"""
    try:
        service = ConversationService(db)
        threads = service.get_threads(session_id, thread_type=thread_type)
        return success_response({"session_id": session_id, "threads": threads})
    except Exception as e:
        return error_response(code="FETCH_FAILED", message=str(e))


@router.post("/threads")
def create_thread(session_id: str, data: dict, db: Session = Depends(get_db)):
    """创建对话线程"""
    try:
        service = ConversationService(db)
        thread_type = data.get("thread_type", "public")
        participant_ids = data.get("participant_ids", [])
        thread = service.create_thread(session_id, thread_type, participant_ids)
        return success_response(thread)
    except Exception as e:
        return error_response(code="CREATE_FAILED", message=str(e))
