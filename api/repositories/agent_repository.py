# -*- coding: utf-8 -*-
"""
Agent 数据访问层
"""
from sqlalchemy.orm import Session
from api.models.agent import Agent, AgentRuntimeState
from typing import Optional, List


class AgentRepository:
    """Agent 仓库 - 封装 Agent 相关数据库操作"""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Agent]:
        """获取所有 Agent"""
        return self.db.query(Agent).all()

    def get_by_id(self, agent_id: str) -> Optional[Agent]:
        """根据 ID 获取 Agent"""
        return self.db.query(Agent).filter(Agent.id == agent_id).first()

    def create(self, agent: Agent) -> Agent:
        """创建 Agent"""
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        return agent

    def get_runtime_state(self, session_id: str, agent_id: str) -> Optional[AgentRuntimeState]:
        """获取指定会话和 Agent 的运行时状态"""
        return self.db.query(AgentRuntimeState).filter(
            AgentRuntimeState.session_id == session_id,
            AgentRuntimeState.agent_id == agent_id
        ).first()

    def save_runtime_state(self, state: AgentRuntimeState) -> AgentRuntimeState:
        """保存运行时状态（新增或更新）"""
        self.db.merge(state)
        self.db.commit()
        self.db.refresh(state)
        return state

    def get_runtime_states(self, session_id: str) -> List[AgentRuntimeState]:
        """获取会话的所有 Agent 运行时状态"""
        return self.db.query(AgentRuntimeState).filter(
            AgentRuntimeState.session_id == session_id
        ).all()

    def create_runtime_state(self, state: AgentRuntimeState) -> AgentRuntimeState:
        """创建 Agent 运行时状态"""
        self.db.add(state)
        self.db.commit()
        self.db.refresh(state)
        return state

    def update_runtime_state(self, state: AgentRuntimeState) -> AgentRuntimeState:
        """更新 Agent 运行时状态"""
        self.db.merge(state)
        self.db.commit()
        self.db.refresh(state)
        return state
