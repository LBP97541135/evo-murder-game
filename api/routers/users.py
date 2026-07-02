# -*- coding: utf-8 -*-
"""用户管理路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.db.base import get_db
from api.core.responses import success_response, error_response

router = APIRouter(prefix="/users", tags=["用户"])


@router.get("/profile")
def get_profile(user_id: str = "default", db: Session = Depends(get_db)):
    """获取用户信息"""
    # 用户画像功能暂时保留基础实现
    return success_response({
        "user_id": user_id,
        "display_name": "玩家",
        "level": 1,
        "preferred_genres": [],
        "preferred_difficulty": "medium",
        "total_games": 0,
    })


@router.patch("/profile")
def update_profile(data: dict, user_id: str = "default", db: Session = Depends(get_db)):
    """更新用户信息"""
    # 用户画像更新功能暂时保留基础实现
    return success_response({"message": "用户信息已更新", "user_id": user_id})
