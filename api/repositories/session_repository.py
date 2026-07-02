# -*- coding: utf-8 -*-
"""
游戏会话数据访问层
"""
from sqlalchemy.orm import Session
from api.models.session import GameSession, GamePhaseEvent, GameCast
from typing import Optional, List


class SessionRepository:
    """游戏会话仓库 - 封装游戏会话相关数据库操作"""

    def __init__(self, db: Session):
        self.db = db

    def get_all_sessions(self, status: Optional[str] = None) -> List[GameSession]:
        """获取所有游戏会话（可按状态筛选）"""
        query = self.db.query(GameSession)
        if status:
            query = query.filter(GameSession.status == status)
        return query.all()

    def get_by_id(self, session_id: str) -> Optional[GameSession]:
        """根据 ID 获取游戏会话"""
        return self.db.query(GameSession).filter(GameSession.id == session_id).first()

    def create(self, session: GameSession) -> GameSession:
        """创建游戏会话"""
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def update(self, session: GameSession) -> GameSession:
        """更新游戏会话"""
        self.db.merge(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def add_phase_event(self, event: GamePhaseEvent) -> GamePhaseEvent:
        """添加阶段事件"""
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def create_phase_event(self, event: GamePhaseEvent) -> GamePhaseEvent:
        """添加阶段事件（别名）"""
        return self.add_phase_event(event)

    def get_phase_events(self, session_id: str) -> List[GamePhaseEvent]:
        """获取会话的所有阶段事件"""
        return self.db.query(GamePhaseEvent).filter(GamePhaseEvent.session_id == session_id).all()

    def add_cast(self, cast: GameCast) -> GameCast:
        """添加角色分配"""
        self.db.add(cast)
        self.db.commit()
        self.db.refresh(cast)
        return cast

    def create_cast(self, cast: GameCast) -> GameCast:
        """添加角色分配（别名）"""
        return self.add_cast(cast)

    def get_casts(self, session_id: str) -> List[GameCast]:
        """获取会话的所有角色分配"""
        return self.db.query(GameCast).filter(GameCast.session_id == session_id).all()

    def delete_casts_by_session(self, session_id: str) -> bool:
        """删除会话的所有角色分配"""
        deleted = self.db.query(GameCast).filter(GameCast.session_id == session_id).delete()
        self.db.commit()
        return deleted >= 0
