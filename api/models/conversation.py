from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from api.db.base import Base


def utc_now():
    return datetime.now(timezone.utc)


class ConversationThread(Base):
    __tablename__ = "conversation_threads"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("game_sessions.id"), nullable=False)
    thread_type = Column(String, nullable=False, default="public")
    title = Column(String, default="")
    participant_ids = Column(JSON, default=[])
    status = Column(String, default="active")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    metadata_json = Column(JSON, default={})

    messages = relationship("ConversationMessage", back_populates="thread", cascade="all, delete-orphan")


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("game_sessions.id"), nullable=False)
    thread_id = Column(String, ForeignKey("conversation_threads.id"), nullable=False)
    sender_type = Column(String, nullable=False)
    sender_id = Column(String, default="")
    sender_name = Column(String, default="")
    target_id = Column(String, default="")
    message_type = Column(String, default="text")
    content = Column(Text, nullable=False)
    raw_prompt = Column(Text, default="")
    raw_response = Column(Text, default="")
    critique_response = Column(Text, default="")
    final_response = Column(Text, default="")
    visibility = Column(String, default="public")
    phase = Column(String, default="")
    created_at = Column(DateTime, default=utc_now)
    metadata_json = Column(JSON, default={})

    thread = relationship("ConversationThread", back_populates="messages")