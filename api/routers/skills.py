# -*- coding: utf-8 -*-
"""Skill 管理路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.db.base import get_db
from api.core.responses import success_response, error_response
from api.services.skill_service import SkillService

router = APIRouter(prefix="/skills", tags=["Skill"])


@router.get("/")
def get_skills(category: str = None, status: str = None, db: Session = Depends(get_db)):
    """获取 Skill 列表"""
    try:
        service = SkillService(db)
        skills = service.list_skills(category=category, status=status)
        return success_response({"skills": skills})
    except Exception as e:
        return error_response(code="FETCH_FAILED", message=str(e))


@router.post("/")
def create_skill(data: dict, db: Session = Depends(get_db)):
    """创建 Skill"""
    try:
        service = SkillService(db)
        skill = service.create_skill(data)
        return success_response(skill)
    except Exception as e:
        return error_response(code="CREATE_FAILED", message=str(e))


@router.get("/{skill_id}")
def get_skill(skill_id: str, db: Session = Depends(get_db)):
    """获取 Skill 详情"""
    try:
        service = SkillService(db)
        skill = service.get_skill(skill_id)
        if not skill:
            return error_response(code="NOT_FOUND", message="Skill 不存在", status_code=404)
        return success_response(skill)
    except Exception as e:
        return error_response(code="FETCH_FAILED", message=str(e))


@router.patch("/{skill_id}")
def update_skill(skill_id: str, data: dict, db: Session = Depends(get_db)):
    """更新 Skill"""
    try:
        service = SkillService(db)
        skill = service.update_skill(skill_id, data)
        return success_response(skill)
    except ValueError as e:
        return error_response(code="UPDATE_FAILED", message=str(e))


@router.delete("/{skill_id}")
def delete_skill(skill_id: str, db: Session = Depends(get_db)):
    """删除 Skill"""
    try:
        service = SkillService(db)
        success = service.delete_skill(skill_id)
        if not success:
            return error_response(code="NOT_FOUND", message="Skill 不存在", status_code=404)
        return success_response({"message": "Skill 已删除"})
    except Exception as e:
        return error_response(code="DELETE_FAILED", message=str(e))


@router.post("/search")
def search_skills(data: dict, db: Session = Depends(get_db)):
    """搜索 Skill"""
    try:
        service = SkillService(db)
        role = data.get("role")
        category = data.get("category")
        signals = data.get("signals")
        limit = data.get("limit", 10)
        skills = service.search_skills(role=role, category=category, signals=signals, limit=limit)
        return success_response({"skills": skills})
    except Exception as e:
        return error_response(code="SEARCH_FAILED", message=str(e))


@router.post("/import")
def import_skill(data: dict, db: Session = Depends(get_db)):
    """导入 Skill"""
    try:
        service = SkillService(db)
        skill = service.import_skill(data)
        return success_response(skill)
    except Exception as e:
        return error_response(code="IMPORT_FAILED", message=str(e))


@router.get("/{skill_id}/export")
def export_skill(skill_id: str, db: Session = Depends(get_db)):
    """导出 Skill"""
    try:
        service = SkillService(db)
        data = service.export_skill(skill_id)
        return success_response(data)
    except ValueError as e:
        return error_response(code="EXPORT_FAILED", message=str(e))


@router.post("/{skill_id}/review")
def review_skill(skill_id: str, data: dict, db: Session = Depends(get_db)):
    """审核 Skill"""
    try:
        service = SkillService(db)
        skill = service.get_skill(skill_id)
        if not skill:
            return error_response(code="NOT_FOUND", message="Skill 不存在", status_code=404)
        
        # 更新审核状态
        update_data = {
            "review_status": data.get("status", "draft"),
            "reviewed_by": data.get("reviewed_by", ""),
            "review_comment": data.get("comment", ""),
        }
        skill = service.update_skill(skill_id, update_data)
        return success_response(skill)
    except Exception as e:
        return error_response(code="REVIEW_FAILED", message=str(e))
