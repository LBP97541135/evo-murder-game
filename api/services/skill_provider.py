# -*- coding: utf-8 -*-
"""Skill 提供者抽象接口

核心服务依赖此抽象接口，具体实现可以是本地数据库或外部 Skill 市场。
"""

from abc import ABC, abstractmethod
from typing import Optional


class SkillProvider(ABC):
    """Skill 提供者抽象接口。
    
    核心服务依赖此抽象接口，具体实现可以是本地数据库或外部 Skill 市场。
    """
    
    @abstractmethod
    def search(self, role: str = "", category: str = "", signals: list = None, limit: int = 10) -> list:
        """搜索适用 Skill。
        
        Args:
            role: 角色类型
            category: 分类
            signals: 信号列表
            limit: 返回数量限制
            
        Returns:
            Skill 列表
        """
        ...
    
    @abstractmethod
    def load(self, skill_id: str) -> dict:
        """加载 Skill 内容。
        
        Args:
            skill_id: Skill ID
            
        Returns:
            Skill 内容字典
        """
        ...


__all__ = ["SkillProvider"]
