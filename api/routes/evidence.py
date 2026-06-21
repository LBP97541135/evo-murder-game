"""
EvoMap Murder Game - Evidence System Routes

运行时证物系统：发现、出示、组合、状态查询。
v2.2 新增：LLM 动态生成角色对证物的反应（无预设反应时自动调用）。
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from api.db.models import (
    get_session,
    Script, ScriptEvidence,
    EvidenceRecord, EvidenceReactionRecord, EvidenceDiscoveryRecord,
    EvidencePresentationRecord, EvidenceCombinationRecord, GameProgressRecord,
    evidence_record_to_dict, dict_to_evidence_record,
)

logger = logging.getLogger(__name__)

router = APIRouter()

PUBLIC_PRESENT_TARGETS = {"公开", "所有人", "all", "public"}


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
    id: Optional[str] = None


class EvidenceDiscoverRequest(BaseModel):
    scriptId: str
    sessionId: str
    scriptEvidenceId: str
    discoveredBy: str = "player"


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


class PhaseUpdateRequest(BaseModel):
    phase: str


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
        evidence_id = req.id or f"evidence_{uuid.uuid4().hex[:8]}"

        existing = session.query(EvidenceRecord).filter(
            EvidenceRecord.id == evidence_id,
            EvidenceRecord.session_id == req.sessionId,
        ).first()
        if existing:
            return {
                "success": True,
                "evidence": evidence_record_to_dict(existing),
                "message": "证物已存在",
            }

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
            discovery_method="investigation",
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


@router.post("/discover")
async def discover_script_evidence(req: EvidenceDiscoverRequest):
    """从剧本证物池中发现一条证物（搜证阶段）。"""
    session = get_session()
    try:
        template = session.query(ScriptEvidence).filter(
            ScriptEvidence.id == req.scriptEvidenceId,
            ScriptEvidence.script_id == req.scriptId,
        ).first()
        if not template:
            raise HTTPException(status_code=404, detail="剧本证物不存在")

        existing = session.query(EvidenceRecord).filter(
            EvidenceRecord.id == req.scriptEvidenceId,
            EvidenceRecord.session_id == req.sessionId,
        ).first()
        if existing:
            return {
                "success": True,
                "evidence": evidence_record_to_dict(existing),
                "message": "证物已发现",
            }

        related = template.related_characters
        if isinstance(related, str):
            import json as _json
            try:
                related = _json.loads(related)
            except Exception:
                related = []

        evidence = EvidenceRecord(
            id=template.id,
            script_id=req.scriptId,
            session_id=req.sessionId,
            name=template.name,
            basic_description=template.description or "",
            category=template.category or "physical",
            importance=template.importance or "medium",
            related_actors=related or [],
            discovery_state="surface",
            unlock_level=1,
            is_new=True,
            discovered_at=datetime.now(timezone.utc),
        )
        session.add(evidence)

        discovery = EvidenceDiscoveryRecord(
            evidence_id=template.id,
            session_id=req.sessionId,
            actor_name=req.discoveredBy,
            discovery_method="investigation",
            previous_state="hidden",
            new_state="surface",
        )
        session.add(discovery)
        _update_progress(session, req.sessionId, req.scriptId, discovered=template.id)

        session.commit()
        session.refresh(evidence)

        return {
            "success": True,
            "evidence": evidence_record_to_dict(evidence),
            "message": "搜证成功",
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"搜证失败: {str(e)}")
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
    """向角色出示证物（优先使用预设反应，否则由 LLM 动态生成）。"""
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

        new_evidences = []
        updated_info = []

        if reaction:
            reaction_type = reaction.reaction_type
            ai_response = reaction.basic_response
            new_evidences = reaction.breakthrough.get("unlock_evidences", []) if reaction.breakthrough else []
            updated_info = reaction.breakthrough.get("updated_info", []) if reaction.breakthrough else []
        elif req.presentedTo in PUBLIC_PRESENT_TARGETS:
            reaction_type = "public"
            reason = (req.textContent or "").strip()
            try:
                from api.llm.llm_service import respond_initial

                llm_prompt = (
                    f"你是剧本杀 DM 主持人。玩家向全体公开出示了证物【{evidence.name}】。\n"
                    f"证物描述：{evidence.basic_description or '无'}\n"
                    f"详细描述：{evidence.detailed_description or evidence.deep_description or '无'}\n"
                )
                if reason:
                    llm_prompt += f"玩家出示理由：{reason}\n"
                llm_prompt += (
                    "\n请用 80-120 字描述：\n"
                    "1. 在场众人看到证物后的整体反应\n"
                    "2. 这条证物对当前讨论可能产生什么影响\n"
                    "语气庄重、客观，不要直接泄露凶手身份。"
                )
                ai_response = respond_initial(
                    system_prompt="你是专业剧本杀 DM，擅长描述公开出示证物后众人的反应。",
                    user_message=llm_prompt,
                    temperature=0.7,
                    max_tokens=300,
                )
            except Exception as llm_err:
                logger.warning(f"公开证物反应生成失败: {llm_err}")
                ai_response = (
                    f"（{evidence.name}被公开出示，在场众人的目光都集中在这份证物上，"
                    "讨论的气氛明显紧张了起来。）"
                )
        else:
            # 无预设反应 → 使用 LLM 动态生成角色反应
            reaction_type = "llm_generated"
            try:
                from api.llm.llm_service import respond_initial
                from api.agents.game_engine import game_engine
                from api.agents.game_context import find_agent_key

                agent_state = None
                if evidence.session_id:
                    game = game_engine.get_game(evidence.session_id)
                    if game:
                        agent_key = find_agent_key(game, req.presentedTo)
                        if agent_key:
                            agent_state = game.get("agents", {}).get(agent_key)

                character_context = ""
                if agent_state:
                    ch = agent_state.character
                    character_context = (
                        f"角色名：{ch.get('name', '?')}\n"
                        f"性格：{ch.get('personality', '无')}\n"
                        f"简介：{ch.get('bio', '无')}\n"
                        f"设定：{ch.get('context', '无')}\n"
                    )
                else:
                    character_context = f"角色名：{req.presentedTo}\n"

                reason = (req.textContent or "").strip()
                llm_prompt = (
                    f"你正在扮演一个剧本杀角色。以下是你的角色信息：\n"
                    f"{character_context}\n"
                    f"玩家向你出示了【{evidence.name}】。\n"
                    f"证物描述：{evidence.basic_description or '无'}\n"
                    f"详细描述：{evidence.detailed_description or evidence.deep_description or '无'}\n"
                )
                if reason:
                    llm_prompt += f"玩家出示理由：{reason}\n"
                llm_prompt += (
                    "\n请以角色的身份，用第一人称对出示的证物做出自然反应（50-100字）：\n"
                    "1. 你认识这个证物吗？\n"
                    "2. 你对此有什么反应？（惊讶/回避/承认/混淆等）\n"
                    "3. 你说出的话是否隐瞒了什么？\n"
                    "语气要贴合角色性格。注意：如果证物对角色不利，你可能会狡辩或转移话题。"
                )

                ai_response = respond_initial(
                    system_prompt=(
                        "你是剧本杀中的角色。你的回答必须符合角色性格和当前处境。\n"
                        "玩家出示证物给你时，你的反应应该自然且有角色特色。\n"
                        "不要直接承认自己是凶手，除非证物确凿且角色性格如此。"
                    ),
                    user_message=llm_prompt,
                    temperature=0.8,
                    max_tokens=300,
                )
            except Exception as llm_err:
                logger.warning(f"LLM 证物反应生成失败: {llm_err}")
                ai_response = f"（{req.presentedTo}看着{evidence.name}，神色有些复杂）嗯，这个证物我知道一些情况……但现在不方便多说。"
                reaction_type = "basic"

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

        if evidence.session_id:
            try:
                from api.agents.game_engine import game_engine
                game_engine.record_evidence_presentation(
                    game_id=evidence.session_id,
                    evidence={
                        "id": evidence.id,
                        "name": evidence.name,
                        "description": evidence.basic_description or "",
                    },
                    presented_by=req.presentedBy,
                    presented_to=req.presentedTo,
                    reason=req.textContent or "",
                    ai_response=ai_response,
                )
            except Exception as mem_err:
                logger.warning(f"证物记忆写入失败（非致命）: {mem_err}")

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
async def update_game_phase(session_id: str, req: PhaseUpdateRequest):
    """更新游戏阶段。请求体: {"phase": "investigation"}"""
    session = get_session()
    try:
        progress = session.query(GameProgressRecord).filter(
            GameProgressRecord.session_id == session_id
        ).first()

        if not progress:
            raise HTTPException(status_code=404, detail="进度记录不存在")

        progress.current_phase = req.phase
        progress.last_activity = datetime.now(timezone.utc)
        session.commit()

        return {"success": True, "message": f"游戏阶段已更新为: {req.phase}"}
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