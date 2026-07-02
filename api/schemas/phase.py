# -*- coding: utf-8 -*-
"""
游戏阶段相关 Schema
"""
from pydantic import BaseModel
from typing import Optional


class PhaseResponse(BaseModel):
    """阶段响应"""
    phase: str
    phase_name: str = ""
    description: str = ""
    is_current: bool = False


class PhaseAdvanceRequest(BaseModel):
    """推进阶段请求"""
    session_id: str
    target_phase: str
    reason: str = ""


class PhaseForceRequest(BaseModel):
    """强制跳转阶段请求"""
    session_id: str
    target_phase: str
    reason: str = ""
    force: bool = True
