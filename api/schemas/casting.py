# -*- coding: utf-8 -*-
"""
角色分配相关 Schema
"""
from pydantic import BaseModel
from typing import Optional, List


class CastRequest(BaseModel):
    """角色分配请求"""
    session_id: str
    character_id: str
    actor_type: str  # human / agent / dm
    actor_id: str
    agent_id: str = ""
    user_id: str = ""
    role_name: str = ""
    is_player: bool = False


class CastResponse(BaseModel):
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

    model_config = {"from_attributes": True}
