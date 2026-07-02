# -*- coding: utf-8 -*-
"""
剧本相关 Schema
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ScriptBase(BaseModel):
    """剧本基础字段"""
    title: str
    description: str = ""
    author: str = ""
    version: str = "1.0.0"
    genre: str = ""
    theme: str = ""
    difficulty: str = "medium"
    duration_minutes: int = 120
    player_count: int = 6
    emotion_level: float = 0.0
    inference_level: float = 0.0
    horror_level: float = 0.0
    cover_image: str = ""
    source_type: str = "manual"


class ScriptCreate(ScriptBase):
    """创建剧本请求"""
    id: str


class ScriptResponse(ScriptBase):
    """剧本响应"""
    id: str
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ScriptCharacterResponse(BaseModel):
    """剧本角色响应"""
    id: str
    script_id: str
    name: str
    bio: str = ""
    personality: str = ""
    role_type: str = "suspect"
    is_victim: bool = False
    is_killer: bool = False
    avatar_image: str = ""
    order_index: int = 0

    model_config = {"from_attributes": True}


class ScriptTruthResponse(BaseModel):
    """剧本真相响应"""
    id: str
    script_id: str
    global_story: str = ""
    truth_summary: str = ""
    killer_character_id: str = ""
    motive: str = ""
    method: str = ""
    timeline: str = ""
    reveal_text: str = ""

    model_config = {"from_attributes": True}
