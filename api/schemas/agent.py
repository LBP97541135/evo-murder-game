# -*- coding: utf-8 -*-
"""
Agent 相关 Schema
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AgentResponse(BaseModel):
    """Agent 响应"""
    id: str
    name: str
    role: str
    model: str = ""
    persona_id: str = ""
    status: str = "active"
    domains: List[str] = []
    identity_doc: str = ""
    constitution: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AgentRuntimeStateResponse(BaseModel):
    """Agent 运行时状态响应"""
    id: str
    session_id: str
    agent_id: str
    character_id: str = ""
    phase: str = ""
    short_memory: List = []
    compressed_summary: str = ""
    key_facts: List = []
    known_evidence_ids: List[str] = []
    loaded_skill_ids: List[str] = []
    intent_json: dict = {}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
