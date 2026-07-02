# -*- coding: utf-8 -*-
"""
对话相关 Schema
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MessageCreate(BaseModel):
    """创建消息请求"""
    session_id: str
    thread_id: str
    sender_type: str  # human / agent / dm / system
    sender_id: str = ""
    sender_name: str = ""
    target_id: str = ""
    message_type: str = "text"
    content: str
    visibility: str = "public"


class MessageResponse(BaseModel):
    """消息响应"""
    id: str
    session_id: str
    thread_id: str
    sender_type: str
    sender_id: str = ""
    sender_name: str = ""
    target_id: str = ""
    message_type: str = "text"
    content: str
    final_response: str = ""
    visibility: str = "public"
    phase: str = ""
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ThreadResponse(BaseModel):
    """对话线程响应"""
    id: str
    session_id: str
    thread_type: str
    title: str = ""
    status: str = "active"
    participant_ids: List[str] = []
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
