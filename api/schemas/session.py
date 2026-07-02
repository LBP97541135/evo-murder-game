# -*- coding: utf-8 -*-
"""
游戏会话相关 Schema
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class GameSessionResponse(BaseModel):
    """游戏会话响应"""
    id: str
    script_id: str
    host_user_id: str = ""
    title: str = ""
    current_phase: str = "setup"
    status: str = "active"
    player_character_id: str = ""
    dm_agent_id: str = ""
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class GamePhaseEventResponse(BaseModel):
    """游戏阶段事件响应"""
    id: str
    session_id: str
    from_phase: str = ""
    to_phase: str
    reason: str = ""
    triggered_by: str = ""
    frontend_index: Optional[int] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class GameCastResponse(BaseModel):
    """角色分配响应"""
    id: str
    session_id: str
    character_id: str
    actor_type: str
    actor_id: str
    agent_id: str = ""
    user_id: str = ""
    role_name: str = ""
    is_player: bool = False
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class GameSnapshotResponse(BaseModel):
    """游戏快照响应（会话 + 阶段事件 + 角色分配）"""
    session: GameSessionResponse
    phase_events: List[GamePhaseEventResponse] = []
    casts: List[GameCastResponse] = []
