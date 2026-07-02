# -*- coding: utf-8 -*-
"""
统一响应格式模块

提供标准化的 API 响应格式，确保所有接口返回一致的数据结构。
"""

from typing import Any, Optional
from fastapi.responses import JSONResponse


def success_response(data: Any = None, message: str = "") -> dict:
    """
    构建成功响应
    
    Args:
        data: 响应数据
        message: 响应消息
    
    Returns:
        标准化的成功响应字典
    """
    return {
        "success": True,
        "data": data,
        "message": message,
    }


def error_response(
    code: str,
    message: str,
    details: Optional[dict] = None,
    status_code: int = 400,
) -> JSONResponse:
    """
    构建错误响应
    
    Args:
        code: 错误码
        message: 错误消息
        details: 错误详情
        status_code: HTTP 状态码
    
    Returns:
        JSONResponse 错误响应
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            },
        },
    )


__all__ = ["success_response", "error_response"]
