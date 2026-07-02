# -*- coding: utf-8 -*-
"""选角管理路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.db.base import get_db
from api.core.responses import success_response, error_response
from api.services.casting_service import CastingService

router = APIRouter(prefix="/sessions/{session_id}/cast", tags=["选角"])


@router.post("/")
def set_casting(session_id: str, data: list[dict], db: Session = Depends(get_db)):
    """设置选角"""
    try:
        service = CastingService(db)
        casts = service.cast_session(session_id, data)
        return success_response({"session_id": session_id, "casts": casts})
    except Exception as e:
        return error_response(code="CAST_FAILED", message=str(e))


@router.get("/")
def get_casting(session_id: str, db: Session = Depends(get_db)):
    """获取选角信息"""
    try:
        service = CastingService(db)
        casts = service.get_casts(session_id)
        return success_response({"session_id": session_id, "casts": casts})
    except Exception as e:
        return error_response(code="FETCH_FAILED", message=str(e))


@router.delete("/")
def reset_casting(session_id: str, db: Session = Depends(get_db)):
    """重置选角"""
    try:
        service = CastingService(db)
        service.reset_casts(session_id)
        return success_response({"message": "选角已重置"})
    except Exception as e:
        return error_response(code="RESET_FAILED", message=str(e))
