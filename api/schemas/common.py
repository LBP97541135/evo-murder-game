# -*- coding: utf-8 -*-
"""
通用 Schema 模块

提供分页、统一响应等通用数据结构定义。
"""

from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(default=1, ge=1, description="页码，从 1 开始")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应结构"""
    items: List[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(default=0, description="总记录数")
    page: int = Field(default=1, description="当前页码")
    page_size: int = Field(default=20, description="每页数量")
    total_pages: int = Field(default=0, description="总页数")


class UnifiedResponse(BaseModel, Generic[T]):
    """统一响应结构"""
    success: bool = Field(default=True, description="是否成功")
    data: Optional[T] = Field(default=None, description="响应数据")
    message: str = Field(default="", description="响应消息")
    error: Optional[dict] = Field(default=None, description="错误信息")


__all__ = [
    "PaginationParams",
    "PaginatedResponse",
    "UnifiedResponse",
]
