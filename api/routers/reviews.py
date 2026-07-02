# -*- coding: utf-8 -*-
"""复盘报告路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.db.base import get_db
from api.core.responses import success_response, error_response
from api.services.review_service import ReviewService

router = APIRouter(prefix="/sessions/{session_id}/review", tags=["复盘"])


@router.get("/")
def get_review(session_id: str, db: Session = Depends(get_db)):
    """获取复盘报告"""
    try:
        service = ReviewService(db)
        review = service.get_review(session_id)
        if not review:
            return success_response({"session_id": session_id, "review": None})
        return success_response({"session_id": session_id, "review": review})
    except Exception as e:
        return error_response(code="FETCH_FAILED", message=str(e))


@router.post("/run")
def run_review(session_id: str, db: Session = Depends(get_db)):
    """运行复盘"""
    try:
        service = ReviewService(db)
        result = service.run_review(session_id)
        return success_response(result)
    except Exception as e:
        return error_response(code="RUN_FAILED", message=str(e))
