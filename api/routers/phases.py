# -*- coding: utf-8 -*-
"""游戏阶段路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.db.base import get_db
from api.core.responses import success_response, error_response
from api.services.phase_service import PhaseService

router = APIRouter(prefix="/sessions/{session_id}/phase", tags=["阶段"])


@router.get("/")
def get_current_phase(session_id: str, db: Session = Depends(get_db)):
    """获取当前阶段"""
    try:
        service = PhaseService(db)
        phase = service.get_current_phase(session_id)
        return success_response({"session_id": session_id, "phase": phase})
    except ValueError as e:
        return error_response(code="NOT_FOUND", message=str(e), status_code=404)


@router.post("/advance")
def advance_phase(session_id: str, db: Session = Depends(get_db)):
    """推进阶段"""
    try:
        service = PhaseService(db)
        result = service.advance_phase(session_id)
        return success_response(result)
    except ValueError as e:
        return error_response(code="ADVANCE_FAILED", message=str(e))


@router.post("/force")
def force_phase(session_id: str, data: dict, db: Session = Depends(get_db)):
    """强制跳转阶段"""
    try:
        service = PhaseService(db)
        target_phase = data.get("target_phase")
        reason = data.get("reason", "")
        if not target_phase:
            return error_response(code="MISSING_PARAM", message="缺少 target_phase 参数")
        result = service.force_phase(session_id, target_phase, reason)
        return success_response(result)
    except ValueError as e:
        return error_response(code="FORCE_FAILED", message=str(e))
