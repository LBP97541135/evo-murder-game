# -*- coding: utf-8 -*-
"""证物管理路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.db.base import get_db
from api.core.responses import success_response, error_response
from api.services.evidence_service import EvidenceService

router = APIRouter(prefix="/sessions/{session_id}/evidences", tags=["证物"])


@router.get("/")
def get_evidences(session_id: str, db: Session = Depends(get_db)):
    """获取证物列表"""
    try:
        service = EvidenceService(db)
        evidences = service.get_evidences(session_id)
        return success_response({"session_id": session_id, "evidences": evidences})
    except Exception as e:
        return error_response(code="FETCH_FAILED", message=str(e))


@router.get("/public")
def get_public_evidences(session_id: str, db: Session = Depends(get_db)):
    """获取公开证物"""
    try:
        service = EvidenceService(db)
        evidences = service.get_public_evidences(session_id)
        return success_response({"session_id": session_id, "public_evidences": evidences})
    except Exception as e:
        return error_response(code="FETCH_FAILED", message=str(e))


@router.post("/discover")
def discover_evidence(session_id: str, data: dict, db: Session = Depends(get_db)):
    """发现证物"""
    try:
        service = EvidenceService(db)
        evidence_id = data.get("evidence_id")
        if not evidence_id:
            return error_response(code="MISSING_PARAM", message="缺少 evidence_id 参数")
        evidence = service.discover_evidence(session_id, evidence_id)
        return success_response(evidence)
    except ValueError as e:
        return error_response(code="DISCOVER_FAILED", message=str(e))


@router.post("/present")
def present_evidence(session_id: str, data: dict, db: Session = Depends(get_db)):
    """出示证物"""
    try:
        service = EvidenceService(db)
        evidence_id = data.get("evidence_id")
        presented_to = data.get("presented_to", "")
        is_public = data.get("is_public", False)
        if not evidence_id:
            return error_response(code="MISSING_PARAM", message="缺少 evidence_id 参数")
        evidence = service.present_evidence(session_id, evidence_id, presented_to, is_public)
        return success_response(evidence)
    except ValueError as e:
        return error_response(code="PRESENT_FAILED", message=str(e))


@router.post("/combine")
def combine_evidences(session_id: str, data: dict, db: Session = Depends(get_db)):
    """组合证物"""
    try:
        service = EvidenceService(db)
        evidence_ids = data.get("evidence_ids", [])
        if not evidence_ids or len(evidence_ids) < 2:
            return error_response(code="MISSING_PARAM", message="缺少 evidence_ids 参数或数量不足")
        result = service.combine_evidences(session_id, evidence_ids)
        return success_response(result)
    except ValueError as e:
        return error_response(code="COMBINE_FAILED", message=str(e))
