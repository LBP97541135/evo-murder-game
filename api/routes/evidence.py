"""
EvoMap Murder Game - Evidence System Routes

运行时证物系统：发现、出示、组合、状态查询。
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from api.db.models import (
    get_session,
    EvidenceRecord, EvidenceReactionRecord, EvidenceDiscoveryRecord,
    EvidencePresentationRecord, EvidenceCombinationRecord, GameProgressRecord,
    evidence_record_to_dict, dict_to_evidence_record,
)

router = APIRouter()


# ============================
# 请求/响应模型
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
# 证物查询
# ============================

@router.get("/script/{script_id}/session/{session_id}")
async def get_evidences(
    script_id: str,
    session_id: str,
    category: Optional[str] = Query(None),
    discovery_state: Optional[str] = Query(None),
    importance: Optional[str] = Query(None),
):
    """获取指定游戏会话的全部证物，支持按分类/状态/重要度过滤。"""
    session = get_session()
    try:
        query = session.query(EvidenceRecord).filter(
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

        # 统计信息
        stats = _calculate_stats(evidences)

        return {
            "success": True,
            "evidences": evidence_list,
            "stats": stats,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取证物失败: {str(e)}")
    finally:
        session.close()


# ============================
# 证物创建
# ============================

@router.post("/create")
async def create_evidence(req: EvidenceCreateRequest):
    """创建新证物并记录发现历史。"""
    session = get_session()
    try:
        evidence_id = f"evidence_{uuid.uuid4().hex[:8]}"

        evidence = EvidenceRecord(
            id=evidence_id,
            script_id=req.scriptId,
            session_id=req.sessionId,
            name=req.name,
            basic_description=req.basicDescription,
            category=req.category,
            importance=req.importance,
            related_actors=req.relatedActors,
            discovery_state="surface",
            unlock_level=1,
            is_new=True,
            discovered_at=datetime.now(timezone.utc),
        )
        session.add(evidence)

        # 记录发现
        discovery = EvidenceDiscoveryRecord(
            evidence_id=evidence_id,
            session_id=req.sessionId,
            actor_name=req.discoveredBy,
            discovery_method="system",
            previous_state="hidden",
            new_state="surface",
        )
        session.add(discovery)

        # 更新游戏进度
        _update_progress(session, req.sessionId, req.scriptId, discovered=evidence_id)

        session.commit()
        session.refresh(evidence)

        return {
            "success": True,
            "evidence": evidence_record_to_dict(evidence),
            "message": "证物创建成功",
        }
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"创建证物失败: {str(e)}")
    finally:
        session.close()


# ============================
# 证物更新
# ============================

@router.put("/{evidence_id}")
async def update_evidence(evidence_id: str, req: EvidenceUpdateRequest):
    """更新证物信息（状态/描述/解锁等级等）。"""
    session = get_session()
    try:
        evidence = session.query(EvidenceRecord).filter(EvidenceRecord.id == evidence_id).first()
        if not evidence:
            raise HTTPException(status_code=404, detail="证物不存在")

        previous_state = evidence.discovery_state
        previous_level = evidence.unlock_level

        if req.detailedDescription is not None:
            evidence.detailed_description = req.detailedDescription
            evidence.has_update = True
        if req.deepDescription is not None:
            evidence.deep_description = req.deepDescription
            evidence.has_update = True
        if req.unlockLevel is not None:
            evidence.unlock_level = req.unlockLevel
        if req.discoveryState is not None:
            evidence.discovery_state = req.discoveryState
        if req.relatedActors is not None:
            evidence.related_actors = req.relatedActors
        if req.relatedEvidences is not None:
            evidence.related_evidences = req.relatedEvidences
        if req.importance is not None:
            evidence.importance = req.importance

        evidence.updated_at = datetime.now(timezone.utc)

        # 状态变化时记录发现历史
        if (req.discoveryState and req.discoveryState != previous_state) or \
           (req.unlockLevel and req.unlockLevel != previous_level):
            discovery = EvidenceDiscoveryRecord(
                evidence_id=evidence_id,
                session_id=evidence.session_id,
                actor_name="system",
                discovery_method="investigation",
                previous_state=previous_state,
                new_state=evidence.discovery_state,
            )
            session.add(discovery)

        session.commit()
        session.refresh(evidence)

        return {
            "success": True,
            "evidence": evidence_record_to_dict(evidence),
            "message": "证物更新成功",
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"更新证物失败: {str(e)}")
    finally:
        session.close()


# ============================
# 证物出示
# ============================

@router.post("/present")
async def present_evidence(req: EvidencePresentationRequest):
    """向角色出示证物（返回基础反应，AI 部分由前端层调用 LLM 完成）。"""
    session = get_session()
    try:
        evidence = session.query(EvidenceRecord).filter(EvidenceRecord.id == req.evidenceId).first()
        if not evidence:
            raise HTTPException(status_code=404, detail="证物不存在")

        # 查找预设反应
        reaction = session.query(EvidenceReactionRecord).filter(
            EvidenceReactionRecord.evidence_id == req.evidenceId,
            EvidenceReactionRecord.actor_name == req.presentedTo,
        ).first()

        if reaction:
            reaction_type = reaction.reaction_type
            ai_response = reaction.basic_response
            new_evidences = reaction.breakthrough.get("unlock_evidences", []) if reaction.breakthrough else []
            updated_info = reaction.breakthrough.get("updated_info", []) if reaction.breakthrough else []
        else:
            # 无预设反应时使用通用回应
            reaction_type = "basic"
            ai_response = f"对于{evidence.name}，我没有特别的信息可以提供。"
            new_evidences = []
            updated_info = []

        # 记录出示历史
        presentation = EvidencePresentationRecord(
            evidence_id=req.evidenceId,
            session_id=evidence.session_id,
            presented_to=req.presentedTo,
            presented_by=req.presentedBy,
            text_content=req.textContent or "",
            reaction_type=reaction_type,
            ai_response=ai_response,
            new_evidences_unlocked=new_evidences,
            information_updated=updated_info,
            presentation_context=req.presentationContext or "",
        )
        session.add(presentation)

        # 更新进度
        _update_progress(
            session, evidence.session_id, evidence.script_id,
            presented={req.presentedTo: [req.evidenceId]},
        )

        session.commit()

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
        session.rollback()
        raise HTTPException(status_code=500, detail=f"证物出示失败: {str(e)}")
    finally:
        session.close()


# ============================
# 证物组合
# ============================

@router.post("/combine")
async def combine_evidences(req: EvidenceCombinationRequest):
    """组合两个证物生成新证物。"""
    session = get_session()
    try:
        ev1 = session.query(EvidenceRecord).filter(EvidenceRecord.id == req.primaryEvidenceId).first()
        ev2 = session.query(EvidenceRecord).filter(EvidenceRecord.id == req.secondaryEvidenceId).first()

        if not ev1 or not ev2:
            raise HTTPException(status_code=404, detail="证物不存在")

        # 检查是否可组合
        combinable = ev1.combinable_with or []
        if req.secondaryEvidenceId not in combinable:
            combo = EvidenceCombinationRecord(
                session_id=ev1.session_id,
                primary_evidence_id=req.primaryEvidenceId,
                secondary_evidence_id=req.secondaryEvidenceId,
                combination_success=False,
                combination_result="这两个证物无法组合",
                attempted_by=req.attemptedBy,
            )
            session.add(combo)
            session.commit()
            return {"success": False, "message": "这两个证物无法组合"}

        # 创建组合证物
        combined_id = f"evidence_{uuid.uuid4().hex[:8]}"
        combined = EvidenceRecord(
            id=combined_id,
            script_id=ev1.script_id,
            session_id=ev1.session_id,
            name=f"{ev1.name} + {ev2.name}",
            basic_description=f"通过分析{ev1.name}和{ev2.name}的关联，发现了新的线索。",
            category="combination",
            discovery_state="surface",
            unlock_level=1,
            related_evidences=[ev1.id, ev2.id],
            importance="high",
            is_new=True,
            discovered_at=datetime.now(timezone.utc),
        )
        session.add(combined)

        combo = EvidenceCombinationRecord(
            session_id=ev1.session_id,
            primary_evidence_id=req.primaryEvidenceId,
            secondary_evidence_id=req.secondaryEvidenceId,
            result_evidence_id=combined_id,
            combination_success=True,
            combination_result=f"成功组合生成: {combined.name}",
            attempted_by=req.attemptedBy,
        )
        session.add(combo)

        _update_progress(session, ev1.session_id, ev1.script_id, combined=combined_id)

        session.commit()
        session.refresh(combined)

        return {
            "success": True,
            "evidence": evidence_record_to_dict(combined),
            "message": "证物组合成功",
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"证物组合失败: {str(e)}")
    finally:
        session.close()


# ============================
# 出示历史
# ============================

@router.get("/{evidence_id}/presentations")
async def get_evidence_presentations(evidence_id: str):
    """获取指定证物的出示历史。"""
    session = get_session()
    try:
        records = session.query(EvidencePresentationRecord).filter(
            EvidencePresentationRecord.evidence_id == evidence_id
        ).order_by(EvidencePresentationRecord.presented_at.desc()).all()

        result = []
        for r in records:
            result.append({
                "id": str(r.id),
                "evidenceId": r.evidence_id,
                "sessionId": r.session_id,
                "presentedTo": r.presented_to,
                "presentedBy": r.presented_by,
                "textContent": r.text_content,
                "reactionType": r.reaction_type,
                "aiResponse": r.ai_response,
                "newEvidencesUnlocked": r.new_evidences_unlocked or [],
                "informationUpdated": r.information_updated or [],
                "presentationContext": r.presentation_context,
                "presentedAt": r.presented_at.isoformat() if r.presented_at else None,
            })

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取出示历史失败: {str(e)}")
    finally:
        session.close()


# ============================
# 游戏进度
# ============================

@router.get("/progress/{session_id}")
async def get_game_progress(session_id: str):
    """获取指定游戏会话的进度状态。"""
    session = get_session()
    try:
        progress = session.query(GameProgressRecord).filter(
            GameProgressRecord.session_id == session_id
        ).first()

        if not progress:
            return {
                "success": True,
                "progress": None,
                "message": "暂无进度数据",
            }

        return {
            "success": True,
            "progress": {
                "sessionId": progress.session_id,
                "scriptId": progress.script_id,
                "discoveredEvidences": progress.discovered_evidences or [],
                "presentedEvidences": progress.presented_evidences or {},
                "combinedEvidences": progress.combined_evidences or [],
                "investigatedEvidences": progress.investigated_evidences or [],
                "contradictionsFound": progress.contradictions_found,
                "timeSpent": progress.time_spent,
                "currentPhase": progress.current_phase,
                "hintsUsed": progress.hints_used,
                "updatedAt": progress.updated_at.isoformat() if progress.updated_at else None,
                "lastActivity": progress.last_activity.isoformat() if progress.last_activity else None,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取进度失败: {str(e)}")
    finally:
        session.close()


@router.post("/progress/{session_id}/phase")
async def update_game_phase(session_id: str, phase: str):
    """更新游戏阶段。"""
    session = get_session()
    try:
        progress = session.query(GameProgressRecord).filter(
            GameProgressRecord.session_id == session_id
        ).first()

        if not progress:
            raise HTTPException(status_code=404, detail="进度记录不存在")

        progress.current_phase = phase
        progress.last_activity = datetime.now(timezone.utc)
        session.commit()

        return {"success": True, "message": f"游戏阶段已更新为: {phase}"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"更新阶段失败: {str(e)}")
    finally:
        session.close()


# ============================
# 证物删除
# ============================

@router.delete("/{evidence_id}")
async def delete_evidence(evidence_id: str):
    """删除证物（级联删除关联的发现/出示/组合记录）。"""
    session = get_session()
    try:
        evidence = session.query(EvidenceRecord).filter(EvidenceRecord.id == evidence_id).first()
        if not evidence:
            raise HTTPException(status_code=404, detail="证物不存在")

        session.delete(evidence)
        session.commit()

        return {"success": True, "message": "证物删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"删除证物失败: {str(e)}")
    finally:
        session.close()


# ============================
# 内部辅助
# ============================

def _calculate_stats(evidences: list) -> dict:
    """计算证物统计信息。"""
    total = len(evidences)
    new_count = sum(1 for e in evidences if e.is_new)

    category_breakdown = {}
    state_breakdown = {}
    importance_breakdown = {}

    for e in evidences:
        category_breakdown[e.category] = category_breakdown.get(e.category, 0) + 1
        state_breakdown[e.discovery_state] = state_breakdown.get(e.discovery_state, 0) + 1
        importance_breakdown[e.importance] = importance_breakdown.get(e.importance, 0) + 1

    total_possible = total * 3
    current_levels = sum(e.unlock_level for e in evidences)
    completion = int((current_levels / total_possible) * 100) if total_possible > 0 else 0

    return {
        "totalEvidences": total,
        "newEvidences": new_count,
        "categoryBreakdown": category_breakdown,
        "stateBreakdown": state_breakdown,
        "importanceBreakdown": importance_breakdown,
        "completionRate": completion,
    }


def _update_progress(
    session,
    session_id: str,
    script_id: str,
    discovered: Optional[str] = None,
    presented: Optional[dict] = None,
    combined: Optional[str] = None,
):
    """更新游戏进度（幂等：不存在则创建）。"""
    progress = session.query(GameProgressRecord).filter(
        GameProgressRecord.session_id == session_id
    ).first()

    if not progress:
        progress = GameProgressRecord(
            session_id=session_id,
            script_id=script_id,
            discovered_evidences=[],
            presented_evidences={},
            combined_evidences=[],
            investigated_evidences=[],
        )
        session.add(progress)

    now = datetime.now(timezone.utc)
    progress.last_activity = now

    if discovered:
        lst = list(progress.discovered_evidences or [])
        if discovered not in lst:
            lst.append(discovered)
        progress.discovered_evidences = lst

    if presented:
        d = dict(progress.presented_evidences or {})
        for actor, ev_ids in presented.items():
            existing = list(d.get(actor, []))
            for eid in ev_ids:
                if eid not in existing:
                    existing.append(eid)
            d[actor] = existing
        progress.presented_evidences = d

    if combined:
        lst = list(progress.combined_evidences or [])
        if combined not in lst:
            lst.append(combined)
        progress.combined_evidences = lst