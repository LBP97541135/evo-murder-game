# -*- coding: utf-8 -*-
"""
证物相关 Schema
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EvidenceResponse(BaseModel):
    """证物响应"""
    id: str
    session_id: str
    script_id: str
    name: str
    category: str = ""
    importance: str = "medium"
    basic_description: str = ""
    detailed_description: str = ""
    deep_description: str = ""
    discovery_state: str = "hidden"
    visibility: str = "private"
    owner_character_id: str = ""
    is_public: bool = False
    image_path: str = ""
    unlock_level: int = 1
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class EvidenceDiscoverRequest(BaseModel):
    """发现证物请求"""
    evidence_id: str
    discovery_state: str = "discovered"


class EvidencePresentRequest(BaseModel):
    """展示证物请求"""
    evidence_id: str
    session_id: str
    target_character_id: str = ""
    presentation_type: str = "public"  # public / private
