# -*- coding: utf-8 -*-
"""Agent 记忆提供者抽象接口

核心服务依赖此抽象接口，具体实现可以是本地数据库或 EvoMap。
"""

from abc import ABC, abstractmethod
from typing import Optional


class AgentMemoryProvider(ABC):
    """Agent 记忆提供者抽象接口。
    
    核心服务依赖此抽象接口，具体实现可以是本地数据库或 EvoMap。
    """
    
    @abstractmethod
    def record(self, session_id: str, agent_id: str, content: str, metadata: dict = None) -> dict:
        """记录一条 Agent 记忆。
        
        Args:
            session_id: 游戏会话 ID
            agent_id: Agent ID
            content: 记忆内容
            metadata: 附加元数据
            
        Returns:
            记录结果字典
        """
        ...
    
    @abstractmethod
    def recall(self, session_id: str, agent_id: str, query: str = "", limit: int = 10) -> list:
        """召回 Agent 记忆。
        
        Args:
            session_id: 游戏会话 ID
            agent_id: Agent ID
            query: 查询关键词
            limit: 返回数量限制
            
        Returns:
            记忆列表
        """
        ...


__all__ = ["AgentMemoryProvider"]
