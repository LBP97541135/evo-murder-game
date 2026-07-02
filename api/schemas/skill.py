# -*- coding: utf-8 -*-
"""
Skill 相关 Schema
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SkillCreate(BaseModel):
    """创建 Skill 请求"""
    id: str
    name: str
    version: str = "1.0.0"
    type: str = "prompt_skill"
    category: str = ""
    applicable_roles: List[str] = []
    signals: List[str] = []
    description: str = ""
    prompt_content: str = ""
    strategy: str = ""
    examples: str = ""
    anti_patterns: str = ""
    source_type: str = "manual"
    injection_mode: str = "append_system_prompt"
    injection_priority: int = 50
    max_tokens: int = 800


class SkillResponse(BaseModel):
    """Skill 响应"""
    id: str
    name: str
    version: str = "1.0.0"
    type: str = "prompt_skill"
    category: str = ""
    applicable_roles: List[str] = []
    signals: List[str] = []
    description: str = ""
    prompt_content: str = ""
    strategy: str = ""
    examples: str = ""
    anti_patterns: str = ""
    source_type: str = "manual"
    source_experience_id: str = ""
    source_session_id: str = ""
    source_script_id: str = ""
    created_by_agent_id: str = ""
    quality_score: float = 0.0
    effectiveness_score: float = 0.0
    review_status: str = "draft"
    injection_mode: str = "append_system_prompt"
    injection_priority: int = 50
    max_tokens: int = 800
    usage_count: int = 0
    success_count: int = 0
    last_used_at: Optional[datetime] = None
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SkillSearchRequest(BaseModel):
    """Skill 搜索请求"""
    role: Optional[str] = None
    category: Optional[str] = None
    signals: Optional[List[str]] = None
    limit: int = 10


class SkillImportRequest(BaseModel):
    """Skill 导入请求"""
    skills: List[SkillCreate]


class ExperienceResponse(BaseModel):
    """经验记录响应"""
    id: str
    session_id: str = ""
    script_id: str = ""
    agent_id: str = ""
    role: str = ""
    category: str = ""
    signals: List = []
    status: str = "success"
    self_score: float = 0.0
    summary: str = ""
    detail: str = ""
    dm_reviewed: bool = False
    dm_score: float = 0.0
    dm_comment: str = ""
    dm_suggestions: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
