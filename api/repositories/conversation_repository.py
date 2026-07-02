# -*- coding: utf-8 -*-
"""
对话数据访问层
"""
from sqlalchemy.orm import Session
from api.models.conversation import ConversationThread, ConversationMessage
from typing import Optional, List


class ConversationRepository:
    """对话仓库 - 封装对话相关数据库操作"""

    def __init__(self, db: Session):
        self.db = db

    def create_thread(self, thread: ConversationThread) -> ConversationThread:
        """创建对话线程"""
        self.db.add(thread)
        self.db.commit()
        self.db.refresh(thread)
        return thread

    def get_threads(self, session_id: str, thread_type: Optional[str] = None) -> List[ConversationThread]:
        """获取会话的所有对话线程（可按类型筛选）"""
        query = self.db.query(ConversationThread).filter(ConversationThread.session_id == session_id)
        if thread_type:
            query = query.filter(ConversationThread.thread_type == thread_type)
        return query.all()

    def add_message(self, message: ConversationMessage) -> ConversationMessage:
        """添加消息"""
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def create_message(self, message: ConversationMessage) -> ConversationMessage:
        """添加消息（别名）"""
        return self.add_message(message)

    def get_messages(
        self,
        session_id: str,
        thread_id: Optional[str] = None,
        limit: int = 50
    ) -> List[ConversationMessage]:
        """获取消息列表（可按线程筛选，限制数量）"""
        query = self.db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session_id
        )
        if thread_id:
            query = query.filter(ConversationMessage.thread_id == thread_id)
        return query.order_by(ConversationMessage.created_at.desc()).limit(limit).all()
