# -*- coding: utf-8 -*-
"""
复盘相关 Schema
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ReviewReportResponse(BaseModel):
    """复盘报告响应"""
    id: str
    session_id: str
    status: str = "pending"
    truth_summary: str = ""
    player_result_json: dict = {}
    key_clues_json: List = []
    timeline_json: List = []
    report_content: str = ""
    generated_by: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ReviewRunRequest(BaseModel):
    """触发复盘请求"""
    session_id: str
    generated_by: str = ""
