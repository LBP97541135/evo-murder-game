"""
EvoMap Murder Game - Evidence Routes

游戏运行时的证据 CRUD、出示、组合等操作。
从 ai-murder-mystery 的 evidence_api.py 迁移核心游戏流程。
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from api.db.models import (
    EvidenceRecord, EvidenceReactionRecord,
    EvidenceDiscoveryRecord, EvidencePresentationRecord,
    EvidenceCombinationRecord, GameProgressRecord,
    get_db,
    evidence_record_to_dict,
    presentation_record_to_dict,
)

router = APIRouter()


# ============================
# Request/Response Models
# ============================

class EvidenceCreateRequest(BaseModel):
    scriptId: str
    sessionId: str
    name: str
    basicDescription: str
    category: str = "physical"
    importance: str = "medium"
    relatedActors: List[str] = []
    discoveredBy: str = "system"


class EvidenceUpdateRequest(BaseModel):
    detailedDescription: Optional[str] = None
    deepDescription: Optional[str] = None
    unlockLevel: Optional[int] = None
    discoveryState: Optional[str] = None
    relatedActors: Optional[List[str]] = None
    relatedEvidences: Optional[List[str]] = None
    importance: Optional[str] = None


class EvidencePresentationRequest(BaseModel):
    evidenceId: str
    presentedTo: str
    presentedBy: str
    textContent: Optional[str] = None
    presentationContext: Optional[str] = None


class EvidenceCombinationRequest(BaseModel):
    primaryEvidenceId: str
    secondaryEvidenceId: str
    attemptedBy: str


# ============================
# CRUD Endpoints
# ============================

@router.get("/script/{script_id}/session/{session_id}")
async def get_evidences(
    script_id: str,
    session_id: str,
    category: Optional[str] = None,
    discovery_state: Optional[str] = None,
    importance: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """获取指定剧本会话的所有证物。"""
    try:
        query = db.query(EvidenceRecord).filter(
            EvidenceRecord.script_id == script_id,
            EvidenceRecord.session_id == session_id,
        )

        if category:
            query = query.filter(EvidenceRecord.category == category)
        if discovery_state:
            query = query.filter(EvidenceRecord.discovery_state == discovery_state)
        if importance:
            query = query.filter(EvidenceRecord.importance == importance)

        evidences = query.order_by(EvidenceRecord.updated_at.desc()).all()
        evidence_list = [evidence_record_to_dict(e) for e in evidences]
        stats = calculate_evidence_stats(evidences)

        return {"success": True, "evidences": evidence_list, "stats": stats}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取证物失败: {str(e)}")


@router.post("/create")
async def create_evidence(request: EvidenceCreateRequest, db: Session = Depends(get_db)):
    """创建新证物。"""
    try:
        evidence_id = f"evidence_{uuid.uuid4().hex[:8]}"

        evidence = EvidenceRecord(
            id=evidence_id,
            script_id=request.scriptId,
            session_id=request.sessionId,
            name=request.name,
            basic_description=request.basicDescription,
            category=request.category,
            importance=request.importance,
            related_actors=request.relatedActors,
            discovery_state="surface",
            unlock_level=1,
            is_new=True,
            discovered_at=datetime.now(timezone.utc),
        )
        db.add(evidence)

        discovery = EvidenceDiscoveryRecord(
            evidence_id=evidence_id,
            session_id=request.sessionId,
            actor_name=request.discoveredBy,
            discovery_method="system",
            previous_state="hidden",
            new_state="surface",
        )
        db.add(discovery)

        db.commit()
        db.refresh(evidence)

        return {"success": True, "evidence": evidence_record_to_dict(evidence), "message": "证物创建成功"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建证物失败: {str(e)}")


@router.put("/{evidence_id}")
async def update_evidence(evidence_id: str, request: EvidenceUpdateRequest, db: Session = Depends(get_db)):
    """更新证物信息。"""
    try:
        evidence = db.query(EvidenceRecord).filter(EvidenceRecord.id == evidence_id).first()
        if not evidence:
            raise HTTPException(status_code=404, detail="证物不存在")

        previous_state = evidence.discovery_state
        previous_level = evidence.unlock_level

        if request.detailedDescription is not None:
            evidence.detailed_description = request.detailedDescription
            evidence.has_update = True
        if request.deepDescription is not None:
            evidence.deep_description = request.deepDescription
            evidence.has_update = True
        if request.unlockLevel is not None:
            evidence.unlock_level = request.unlockLevel
        if request.discoveryState is not None:
            evidence.discovery_state = request.discoveryState
        if request.relatedActors is not None:
            evidence.related_actors = request.relatedActors
        if request.relatedEvidences is not None:
            evidence.related_evidences = request.relatedEvidences
        if request.importance is not None:
            evidence.importance = request.importance

        evidence.updated_at = datetime.now(timezone.utc)

        # 状态变更时记录发现历史
        if (request.discoveryState and request.discoveryState != previous_state) or \
           (request.unlockLevel and request.unlockLevel != previous_level):
            discovery = EvidenceDiscoveryRecord(
                evidence_id=evidence_id,
                session_id=evidence.session_id,
                actor_name="system",
                discovery_method="investigation",
                previous_state=previous_state,
                new_state=evidence.discovery_state,
            )
            db.add(discovery)

        db.commit()
        db.refresh(evidence)

        return {"success": True, "evidence": evidence_record_to_dict(evidence), "message": "证物更新成功"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新证物失败: {str(e)}")


@router.delete("/{evidence_id}")
async def delete_evidence(evidence_id: str, db: Session = Depends(get_db)):
    """删除证物。"""
    try:
        evidence = db.query(EvidenceRecord).filter(EvidenceRecord.id == evidence_id).first()
        if not evidence:
            raise HTTPException(status_code=404, detail="证物不存在")
        db.delete(evidence)
        db.commit()
        return {"success": True, "message": "证物删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除证物失败: {str(e)}")


# ============================
# 出示证物（核心游戏交互）
# ============================

@router.post("/present")
async def present_evidence_to_actor(request: EvidencePresentationRequest, db: Session = Depends(get_db)):
    """向角色出示证物并获取AI反应。

    这是证据系统的核心交互端点：
    1. 获取证物信息
    2. 调用 evidence_llm_service 生成角色反应
    3. 解析反应类型（basic/contradiction/breakthrough）
    4. 记录出示历史
    5. 可能解锁新证物或更新信息
    """
    try:
        evidence = db.query(EvidenceRecord).filter(EvidenceRecord.id == request.evidenceId).first()
        if not evidence:
            raise HTTPException(status_code=404, detail="证物不存在")

        # 调用AI生成反应（evidence_llm_service 在 api/llm/ 下，别人负责）
        # 这里我们只构建请求参数，实际的LLM调用由 evidence_llm_service 完成
        from api.llm.evidence_llm_service import invoke_ai_for_evidence_presentation

        ai_response, reaction_type, new_evidences, updated_info = await invoke_ai_for_evidence_presentation(
            evidence_record_to_dict(evidence),
            request.presentedTo,
            request.presentedBy,
            request.textContent,
            request.presentationContext,
        )

        # 记录出示历史
        presentation = EvidencePresentationRecord(
            evidence_id=request.evidenceId,
            session_id=evidence.session_id,
            presented_to=request.presentedTo,
            presented_by=request.presentedBy,
            text_content=request.textContent,
            reaction_type=reaction_type,
            ai_response=ai_response,
            new_evidences_unlocked=new_evidences,
            information_updated=updated_info,
            presentation_context=request.presentationContext,
        )
        db.add(presentation)

        # 处理证物更新（新证物解锁、信息更新）
        if new_evidences or updated_info:
            await process_evidence_updates(db, evidence.session_id, new_evidences, updated_info)

        db.commit()

        return {
            "success": True,
            "aiResponse": ai_response,
            "reactionType": reaction_type,
            "newEvidencesUnlocked": new_evidences,
            "informationUpdated": updated_info,
            "message": "证物出示成功",
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"证物出示失败: {str(e)}")


@router.get("/{evidence_id}/presentations")
async def get_evidence_presentations(evidence_id: str, db: Session = Depends(get_db)):
    """获取证物的出示历史。"""
    try:
        presentations = db.query(EvidencePresentationRecord).filter(
            EvidencePresentationRecord.evidence_id == evidence_id
        ).order_by(EvidencePresentationRecord.presented_at.desc()).all()
        return [presentation_record_to_dict(p) for p in presentations]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取出示历史失败: {str(e)}")


# ============================
# 证物组合
# ============================

@router.post("/combine")
async def combine_evidences(request: EvidenceCombinationRequest, db: Session = Depends(get_db)):
    """组合两个证物产生新证物。"""
    try:
        evidence1 = db.query(EvidenceRecord).filter(EvidenceRecord.id == request.primaryEvidenceId).first()
        evidence2 = db.query(EvidenceRecord).filter(EvidenceRecord.id == request.secondaryEvidenceId).first()

        if not evidence1 or not evidence2:
            raise HTTPException(status_code=404, detail="证物不存在")

        # 检查是否可组合
        if request.secondaryEvidenceId not in (evidence1.combinable_with or []):
            combination = EvidenceCombinationRecord(
                session_id=evidence1.session_id,
                primary_evidence_id=request.primaryEvidenceId,
                secondary_evidence_id=request.secondaryEvidenceId,
                combination_success=False,
                combination_result="这两个证物无法组合",
                attempted_by=request.attemptedBy,
            )
            db.add(combination)
            db.commit()
            return {"success": False, "message": "这两个证物无法组合"}

        # 生成组合证物
        combined_evidence = await generate_combined_evidence(evidence1, evidence2)
        db.add(combined_evidence)

        combination = EvidenceCombinationRecord(
            session_id=evidence1.session_id,
            primary_evidence_id=request.primaryEvidenceId,
            secondary_evidence_id=request.secondaryEvidenceId,
            result_evidence_id=combined_evidence.id,
            combination_success=True,
            combination_result=f"成功组合生成: {combined_evidence.name}",
            attempted_by=request.attemptedBy,
        )
        db.add(combination)

        db.commit()
        db.refresh(combined_evidence)

        return {"success": True, "evidence": evidence_record_to_dict(combined_evidence), "message": "证物组合成功"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"证物组合失败: {str(e)}")


# ============================
# 辅助函数
# ============================

def calculate_evidence_stats(evidences: List[EvidenceRecord]) -> Dict[str, Any]:
    """计算证物统计信息。"""
    total = len(evidences)
    new_count = sum(1 for e in evidences if e.is_new)

    category_breakdown = {}
    state_breakdown = {}
    importance_breakdown = {}

    for evidence in evidences:
        category_breakdown[evidence.category] = category_breakdown.get(evidence.category, 0) + 1
        state_breakdown[evidence.discovery_state] = state_breakdown.get(evidence.discovery_state, 0) + 1
        importance_breakdown[evidence.importance] = importance_breakdown.get(evidence.importance, 0) + 1

    total_possible_levels = total * 3
    current_levels = sum(e.unlock_level for e in evidences)
    completion_rate = int((current_levels / total_possible_levels) * 100) if total_possible_levels > 0 else 0

    return {
        "totalEvidences": total,
        "newEvidences": new_count,
        "categoryBreakdown": category_breakdown,
        "stateBreakdown": state_breakdown,
        "importanceBreakdown": importance_breakdown,
        "completionRate": completion_rate,
    }


async def process_evidence_updates(db: Session, session_id: str, new_evidences: List[str], updated_info: List[str]):
    """处理证物更新逻辑——新证物解锁和信息更新。"""
    # 占位：后续可扩展为自动创建新证物、更新现有证物信息等
    pass


async def generate_combined_evidence(evidence1: EvidenceRecord, evidence2: EvidenceRecord) -> EvidenceRecord:
    """生成组合证物。"""
    combined_id = f"combined_{evidence1.id}_{evidence2.id}_{uuid.uuid4().hex[:4]}"

    combined_evidence = EvidenceRecord(
        id=combined_id,
        script_id=evidence1.script_id,
        session_id=evidence1.session_id,
        name=f"{evidence1.name} + {evidence2.name}",
        basic_description=f"通过分析{evidence1.name}和{evidence2.name}的关联，发现了新的线索。",
        category="combination",
        discovery_state="surface",
        unlock_level=1,
        related_evidences=[evidence1.id, evidence2.id],
        importance="high",
        is_new=True,
        discovered_at=datetime.now(timezone.utc),
    )

    return combined_evidence
