# -*- coding: utf-8 -*-
"""
统一错误定义模块

提供应用级别的错误基类和常见错误类型。
"""

from typing import Optional


class AppError(Exception):
    """
    应用错误基类
    
    所有业务错误都应该继承此类，提供统一的错误码、消息和状态码。
    """
    
    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[dict] = None,
        status_code: int = 400,
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    """资源未找到错误"""
    
    def __init__(self, resource: str, id: str = ""):
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} not found",
            details={"resource": resource, "id": id},
            status_code=404,
        )


class ValidationError(AppError):
    """数据验证错误"""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            details=details,
            status_code=422,
        )


class GameError(AppError):
    """游戏逻辑错误"""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            code="GAME_ERROR",
            message=message,
            details=details,
            status_code=400,
        )


__all__ = [
    "AppError",
    "NotFoundError",
    "ValidationError",
    "GameError",
]
