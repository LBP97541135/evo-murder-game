# -*- coding: utf-8 -*-
"""Internal implementation."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.db.base import get_db
from api.core.responses import success_response, error_response
from api.repositories.script_repository import ScriptRepository

router = APIRouter(prefix="/scripts", tags=["鍓ф湰"])


@router.get("/")
def get_scripts(status: str = "active", db: Session = Depends(get_db)):
    """Internal implementation."""
    try:
        repo = ScriptRepository(db)
        scripts = repo.get_all(status=status)
        return success_response({"scripts": scripts})
    except Exception as e:
        return error_response(code="FETCH_FAILED", message=str(e))


@router.get("/{script_id}")
def get_script(script_id: str, db: Session = Depends(get_db)):
    """Internal implementation."""
    try:
        repo = ScriptRepository(db)
        script = repo.get_by_id(script_id)
        if not script:
            return error_response(code="NOT_FOUND", message="Not found", status_code=404)
        characters = repo.get_characters(script_id)
        truth = repo.get_truth(script_id)
        return success_response({
            "script": script,
            "characters": characters,
            "truth": truth,
        })
    except Exception as e:
        return error_response(code="FETCH_FAILED", message=str(e))


@router.post("/import")
def import_script(data: dict, db: Session = Depends(get_db)):
    """Internal implementation."""
    try:
        from api.models.script import Script
        from datetime import datetime, timezone
        import uuid
        repo = ScriptRepository(db)
        script = Script(
            id=data.get("id") or f"script_{uuid.uuid4().hex[:8]}",
            title=data.get("title", ""),
            description=data.get("description", ""),
            author=data.get("author", ""),
            version=data.get("version", "1.0.0"),
            genre=data.get("genre", ""),
            theme=data.get("theme", ""),
            difficulty=data.get("difficulty", "medium"),
            duration_minutes=data.get("duration_minutes", 120),
            player_count=data.get("player_count", 6),
            emotion_level=data.get("emotion_level", 0.0),
            inference_level=data.get("inference_level", 0.0),
            horror_level=data.get("horror_level", 0.0),
            cover_image=data.get("cover_image", ""),
            source_type=data.get("source_type", "manual"),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        script = repo.create(script)
        return success_response(script)
    except Exception as e:
        return error_response(code="IMPORT_FAILED", message=str(e))
