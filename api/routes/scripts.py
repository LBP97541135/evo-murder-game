"""
EvoMap Murder Game - Script CRUD Routes

剧本的列表、详情。
"""

import json
import os
import base64 as b64_lib
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from api.db.models import (
    get_session,
    Script, Character, QuizQuestion, ScriptEvidence,
    script_to_dict, dict_to_script, dict_to_character,
    dict_to_quiz_question, dict_to_script_evidence,
)

router = APIRouter()

# 初始公开证物（其余默认为搜证池）。锈铁等剧本曾将全部证物误标为 surface，需白名单区分。
SCRIPT_INITIAL_EVIDENCE_IDS: dict[str, set[str]] = {
    "xiutie-avenue-missing-three-minutes": {
        "ev_anonymous_letter",
        "ev_anonymous_letters",
        "ev_safety_report",
        "ev_factory_map",
    },
}


# ============================
# API 端点
# ============================


@router.get("/list")
async def list_scripts():
    """获取所有剧本列表（按更新时间倒序）。"""
    session = get_session()
    try:
        scripts = session.query(Script).order_by(Script.updated_at.desc()).all()
        scripts_data = [script_to_dict(s) for s in scripts]

        return {
            "success": True,
            "scripts": scripts_data,
            "count": len(scripts_data),
        }
    except Exception as e:
        print(f"[scripts] 获取剧本列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取剧本列表失败: {str(e)}")
    finally:
        session.close()


@router.get("/{script_id}")
async def get_script(script_id: str):
    """获取指定剧本的完整数据（含角色/证物/题目）。"""
    session = get_session()
    try:
        script = session.query(Script).filter(Script.id == script_id).first()
        if not script:
            raise HTTPException(status_code=404, detail="剧本不存在")

        return {
            "success": True,
            "script": script_to_dict(script),
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[scripts] 获取剧本失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取剧本失败: {str(e)}")
    finally:
        session.close()


@router.get("/{script_id}/evidence-pool")
async def get_evidence_pool(script_id: str):
    """获取剧本的全部证物池——前端搜证阶段使用。

    返回所有 ScriptEvidence 记录，按 initial_state 分类：
    - "surface" → 初始证物（游戏开始时自动获得）
    - 其他 → 可搜索证物（搜证阶段随机发现）
    """
    session = get_session()
    try:
        script = session.query(Script).filter(Script.id == script_id).first()
        if not script:
            raise HTTPException(status_code=404, detail="剧本不存在")

        evidences = list(script.script_evidences)

        initial_evidences = []
        search_evidences = []
        initial_ids = SCRIPT_INITIAL_EVIDENCE_IDS.get(script_id)

        for e in evidences:
            related = json.loads(e.related_characters) if isinstance(e.related_characters, str) else (e.related_characters or [])
            evidence_dict = {
                "id": e.id,
                "name": e.name,
                "description": e.description or "",
                "category": e.category or "physical",
                "importance": e.importance or "medium",
                "initialState": e.initial_state or "hidden",
                "relatedCharacters": related,
                "image": e.image_filename or "",
            }
            if initial_ids is not None:
                if e.id in initial_ids:
                    initial_evidences.append(evidence_dict)
                else:
                    search_evidences.append(evidence_dict)
            elif e.initial_state == "surface":
                initial_evidences.append(evidence_dict)
            else:
                search_evidences.append(evidence_dict)

        return {
            "success": True,
            "script_id": script_id,
            "initial_evidences": initial_evidences,
            "search_evidences": search_evidences,
            "total_count": len(evidences),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取证物池失败: {str(e)}")
    finally:
        session.close()
