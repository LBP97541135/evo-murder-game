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
