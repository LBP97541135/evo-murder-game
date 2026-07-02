# -*- coding: utf-8 -*-
"""健康检查路由"""

from fastapi import APIRouter
from api.core.responses import success_response

router = APIRouter()


@router.get("/health")
def health_check():
    """健康检查接口"""
    return success_response({"status": "ok", "version": "2.0.0"})
