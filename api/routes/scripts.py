"""
EvoMap Murder Game - Script CRUD Routes

剧本的保存、列表、详情、删除。
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
# 请求/响应模型
# ============================

class ScriptSaveRequest(BaseModel):
    """保存剧本请求——直接接收前端剧本编辑器输出的完整 JSON。"""
    id: str = ""
    title: str = ""
    description: str = ""
    author: str = ""
    version: str = "1.0.0"
    globalStory: str = ""
    sourceType: str = "manual"
    coverImage: str = ""
    coverImageFilename: str = ""
    theme: str = "modern"
    difficulty: str = "medium"
    duration: int = 120
    emotionLevel: float = 0.5
    inferenceLevel: float = 0.5
    horrorLevel: float = 0.0
    playerCount: int = 6
    fixedKiller: str = ""
    characters: list = []
    evidences: list = []
    quiz: list = []
    settings: dict = {}


# ============================
# 辅助
# ============================

def _save_cover_image(script_id: str, cover_data: str) -> str:
    """将 base64 封面保存到文件系统，返回文件名。"""
    if not cover_data or not cover_data.startswith("data:image/"):
        return ""

    try:
        # 解析 base64 数据
        header, encoded = cover_data.split(",", 1)
        image_data = b64_lib.b64decode(encoded)

        timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
        filename = f"script_cover_{script_id}_{timestamp}.png"

        # 保存到 web/public/script_covers/
        web_dir = os.path.join(os.path.dirname(__file__), "..", "..", "web")
        public_dir = os.path.join(web_dir, "public", "script_covers")
        os.makedirs(public_dir, exist_ok=True)

        filepath = os.path.join(public_dir, filename)
        with open(filepath, "wb") as f:
            f.write(image_data)

        return filename
    except Exception as e:
        print(f"[scripts] 保存封面文件失败: {e}")
        return ""


# ============================
# API 端点
# ============================

@router.post("/save")
async def save_script(req: ScriptSaveRequest):
    """保存剧本到数据库（新建或更新）。"""
    print(f"[scripts] 保存剧本: {req.title} (id={req.id})")

    data = req.model_dump()
    script_id = data.get("id", "")
    if not script_id:
        raise HTTPException(status_code=400, detail="剧本ID不能为空")

    session = get_session()
    try:
        existing = session.query(Script).filter(Script.id == script_id).first()

        if existing:
            script = dict_to_script(data, existing)
        else:
            script = dict_to_script(data)
            session.add(script)

        # 处理封面 base64 → 文件
        cover = data.get("coverImage", "")
        if cover and cover.startswith("data:image/"):
            filename = _save_cover_image(script_id, cover)
            if filename:
                script.cover_image = f"/script_covers/{filename}"
                script.cover_image_filename = filename
        elif cover and cover.startswith("/script_covers/"):
            script.cover_image = cover
            script.cover_image_filename = cover.replace("/script_covers/", "")

        # 删除旧子数据（如果是更新）
        if existing:
            session.query(Character).filter(Character.script_id == script_id).delete()
            session.query(QuizQuestion).filter(QuizQuestion.script_id == script_id).delete()
            session.query(ScriptEvidence).filter(ScriptEvidence.script_id == script_id).delete()

        # 保存角色
        for ch_data in data.get("characters", []):
            character = dict_to_character(ch_data, script_id)
            session.add(character)

        # 保存推理题
        for i, q_data in enumerate(data.get("quiz", [])):
            quiz = dict_to_quiz_question(q_data, script_id, i)
            session.add(quiz)

        # 保存证物定义
        for ev_data in data.get("evidences", []):
            evidence = dict_to_script_evidence(ev_data, script_id)
            session.add(evidence)

        session.commit()
        print(f"[scripts] 剧本保存成功: {script.title}")

        return {
            "success": True,
            "message": "剧本保存成功",
            "script_id": script_id,
            "cover_filename": script.cover_image_filename or "",
        }

    except Exception as e:
        session.rollback()
        print(f"[scripts] 保存剧本失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存剧本失败: {str(e)}")
    finally:
        session.close()


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


@router.delete("/{script_id}")
async def delete_script(script_id: str):
    """删除指定剧本及其所有关联数据（角色/题目/证物/剧透故事）。"""
    session = get_session()
    try:
        script = session.query(Script).filter(Script.id == script_id).first()
        if not script:
            raise HTTPException(status_code=404, detail="剧本不存在")

        title = script.title

        # 删除封面文件
        if script.cover_image_filename:
            try:
                web_dir = os.path.join(os.path.dirname(__file__), "..", "..", "web")
                cover_path = os.path.join(web_dir, "public", "script_covers", script.cover_image_filename)
                if os.path.exists(cover_path):
                    os.remove(cover_path)
            except Exception as e:
                print(f"[scripts] 删除封面文件失败: {e}")

        session.delete(script)
        session.commit()

        print(f"[scripts] 删除剧本成功: {title}")
        return {"success": True, "message": "剧本删除成功"}

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        print(f"[scripts] 删除剧本失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除剧本失败: {str(e)}")
    finally:
        session.close()