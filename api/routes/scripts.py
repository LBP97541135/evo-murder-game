"""
EvoMap Murder Game - Script CRUD Routes

剧本的保存、列表、获取、删除，以及证物和剧透故事管理。
从 ai-murder-mystery 的 database_api.py 和 spoiler_story_api.py 迁移核心游戏流程。
"""

import json
import base64
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from api.db.models import (
    Script, Character, QuizQuestion, ScriptEvidence, SpoilerStory,
    get_db, create_tables,
    script_to_dict, dict_to_script,
    dict_to_character, dict_to_script_evidence,
    script_evidence_to_dict, quiz_question_to_dict,
)

router = APIRouter()

# 确保数据库表存在
create_tables()


# ============================
# 剧本 CRUD
# ============================

@router.post("/scripts/save")
async def save_script_to_db(script_data: Dict[str, Any], db: Session = Depends(get_db)):
    """保存剧本到数据库（含角色、题目、证物）。"""
    try:
        script_id = script_data.get("id")
        if not script_id:
            raise HTTPException(status_code=400, detail="剧本ID不能为空")

        existing_script = db.query(Script).filter(Script.id == script_id).first()

        if existing_script:
            script = dict_to_script(script_data, existing_script)
        else:
            script = dict_to_script(script_data)
            db.add(script)

        # 处理封面（base64 → 文件）
        cover_image = script_data.get("coverImage")
        if cover_image and cover_image.startswith("data:image/"):
            try:
                base64_data = cover_image.split(",")[1]
                cover_filename = f"script_cover_{script_id}.png"
                cover_dir = Path(__file__).parent.parent.parent.parent / "web" / "public" / "script_covers"
                cover_dir.mkdir(parents=True, exist_ok=True)
                cover_path = cover_dir / cover_filename
                cover_path.write_bytes(base64.b64decode(base64_data))
                script.cover_image_filename = cover_filename
                script.cover_image_path = f"/script_covers/{cover_filename}"
            except Exception as e:
                print(f"⚠️ 封面保存失败: {e}")

        # 删除旧数据（更新时）
        if existing_script:
            db.query(Character).filter(Character.script_id == script_id).delete()
            db.query(QuizQuestion).filter(QuizQuestion.script_id == script_id).delete()
            db.query(ScriptEvidence).filter(ScriptEvidence.script_id == script_id).delete()

        # 保存角色
        for char_data in script_data.get("characters", []):
            character = dict_to_character(char_data, script_id)
            image = char_data.get("image", "")
            if image and not image.startswith("/character_avatars/"):
                character.image_filename = image
                character.image_path = f"/character_avatars/{image}"
            db.add(character)

        # 保存题目
        for i, quiz_data in enumerate(script_data.get("quiz", [])):
            db.add(dict_to_quiz_question(quiz_data, script_id, i))

        # 保存证物
        for ev_data in script_data.get("evidences", []):
            evidence = dict_to_script_evidence(ev_data, script_id)
            evidence.image_filename = ev_data.get("image", "")
            db.add(evidence)

        db.commit()

        return {
            "success": True,
            "message": "剧本保存成功",
            "script_id": script_id,
            "cover_filename": script.cover_image_filename,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存剧本失败: {str(e)}")


@router.get("/scripts/list")
async def list_scripts_from_db(db: Session = Depends(get_db)):
    """获取所有剧本列表。"""
    try:
        scripts = db.query(Script).order_by(Script.updated_at.desc()).all()
        scripts_data = [script_to_dict(s) for s in scripts]
        return {"success": True, "scripts": scripts_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取剧本列表失败: {str(e)}")


@router.get("/scripts/{script_id}")
async def get_script_from_db(script_id: str, db: Session = Depends(get_db)):
    """获取指定剧本详情。"""
    try:
        script = db.query(Script).filter(Script.id == script_id).first()
        if not script:
            raise HTTPException(status_code=404, detail="剧本不存在")
        return {"success": True, "script": script_to_dict(script)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取剧本失败: {str(e)}")


@router.delete("/scripts/{script_id}")
async def delete_script_from_db(script_id: str, db: Session = Depends(get_db)):
    """删除剧本。"""
    try:
        script = db.query(Script).filter(Script.id == script_id).first()
        if not script:
            raise HTTPException(status_code=404, detail="剧本不存在")

        # 删除封面文件
        if script.cover_image_filename:
            cover_dir = Path(__file__).parent.parent.parent.parent / "web" / "public" / "script_covers"
            cover_path = cover_dir / script.cover_image_filename
            if cover_path.exists():
                cover_path.unlink()

        db.delete(script)
        db.commit()
        return {"success": True, "message": "剧本删除成功"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除剧本失败: {str(e)}")


@router.post("/migrate")
async def migrate_data_to_db(db: Session = Depends(get_db)):
    """数据迁移接口占位。"""
    return {"success": True, "message": "数据迁移接口已准备就绪，请从前端调用"}


# ============================
# 证物管理（剧本级）
# ============================

@router.post("/evidences/save")
async def save_script_evidence(evidence_data: Dict[str, Any], db: Session = Depends(get_db)):
    """保存/更新剧本证物。"""
    try:
        script_id = evidence_data.get("scriptId")
        evidence_id = evidence_data.get("id")
        if not script_id or not evidence_id:
            raise HTTPException(status_code=400, detail="剧本ID和证物ID不能为空")

        script = db.query(Script).filter(Script.id == script_id).first()
        if not script:
            raise HTTPException(status_code=404, detail="剧本不存在")

        existing = db.query(ScriptEvidence).filter(
            ScriptEvidence.id == evidence_id, ScriptEvidence.script_id == script_id
        ).first()

        if existing:
            evidence = dict_to_script_evidence(evidence_data, script_id, existing)
        else:
            evidence = dict_to_script_evidence(evidence_data, script_id)
            db.add(evidence)

        db.commit()
        db.refresh(evidence)
        return {"success": True, "evidence": script_evidence_to_dict(evidence), "message": "证物保存成功"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存证物失败: {str(e)}")


@router.delete("/evidences/{script_id}/{evidence_id}")
async def delete_script_evidence(script_id: str, evidence_id: str, db: Session = Depends(get_db)):
    """删除剧本证物。"""
    try:
        evidence = db.query(ScriptEvidence).filter(
            ScriptEvidence.id == evidence_id, ScriptEvidence.script_id == script_id
        ).first()
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


@router.get("/evidences/{script_id}")
async def get_script_evidences(script_id: str, db: Session = Depends(get_db)):
    """获取剧本的所有证物。"""
    try:
        evidences = db.query(ScriptEvidence).filter(
            ScriptEvidence.script_id == script_id
        ).order_by(ScriptEvidence.created_at.desc()).all()
        data = [script_evidence_to_dict(e) for e in evidences]
        return {"success": True, "evidences": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取证物失败: {str(e)}")


# ============================
# 剧透故事
# ============================

@router.post("/spoiler-stories/save")
async def save_spoiler_story(story_data: Dict[str, Any], db: Session = Depends(get_db)):
    """保存AI生成的剧透故事。"""
    try:
        script_id = story_data.get("scriptId")
        if not script_id:
            raise HTTPException(status_code=400, detail="剧本ID不能为空")

        script = db.query(Script).filter(Script.id == script_id).first()
        if not script:
            raise HTTPException(status_code=404, detail="剧本不存在")

        story = SpoilerStory(
            script_id=script_id,
            title=story_data.get("title", ""),
            content=story_data.get("content", ""),
            word_count=len(story_data.get("content", "")),
            generation_duration=story_data.get("generationDuration", 0.0),
        )

        if not story.title or story.title == "剧透故事":
            story_count = db.query(SpoilerStory).filter(SpoilerStory.script_id == script_id).count()
            story.title = f"《{script.title}》剧透故事 #{story_count + 1}"

        db.add(story)
        db.commit()
        db.refresh(story)

        return {
            "success": True,
            "message": "剧透故事保存成功",
            "story": {
                "id": story.id,
                "scriptId": story.script_id,
                "title": story.title,
                "content": story.content,
                "wordCount": story.word_count,
                "generatedAt": story.generated_at.isoformat() if story.generated_at else None,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"保存剧透故事失败: {str(e)}")


@router.get("/spoiler-stories/{script_id}")
async def get_spoiler_stories(script_id: str, db: Session = Depends(get_db)):
    """获取指定剧本的所有剧透故事。"""
    try:
        script = db.query(Script).filter(Script.id == script_id).first()
        if not script:
            raise HTTPException(status_code=404, detail="剧本不存在")

        stories = db.query(SpoilerStory).filter(
            SpoilerStory.script_id == script_id
        ).order_by(SpoilerStory.generated_at.desc()).all()

        stories_data = [{
            "id": s.id,
            "scriptId": s.script_id,
            "title": s.title,
            "content": s.content,
            "wordCount": s.word_count,
            "generatedAt": s.generated_at.isoformat() if s.generated_at else None,
        } for s in stories]

        return {"success": True, "stories": stories_data, "script_title": script.title}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取剧透故事失败: {str(e)}")
