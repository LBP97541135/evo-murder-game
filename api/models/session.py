from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, String, Text, Integer, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from api.db.base import Base


def utc_now():
    return datetime.now(timezone.utc)


class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(String, primary_key=True)
    script_id = Column(String, ForeignKey("scripts.id"), nullable=False)
    host_user_id = Column(String, default="")
    title = Column(String, default="")
    current_phase = Column(String, nullable=False, default="setup")
    status = Column(String, nullable=False, default="active")
    player_character_id = Column(String, default="")
    dm_agent_id = Column(String, default="")
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    metadata_json = Column(JSON, default={})

    phase_events = relationship("GamePhaseEvent", back_populates="session", cascade="all, delete-orphan")
    casts = relationship("GameCast", back_populates="session", cascade="all, delete-orphan")


class GamePhaseEvent(Base):
    __tablename__ = "game_phase_events"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("game_sessions.id"), nullable=False)
    from_phase = Column(String, default="")
    to_phase = Column(String, nullable=False)
    reason = Column(Text, default="")
    triggered_by = Column(String, default="system")
    frontend_index = Column(Integer)
    created_at = Column(DateTime, default=utc_now)
    metadata_json = Column(JSON, default={})

    session = relationship("GameSession", back_populates="phase_events")


class GameCast(Base):
    __tablename__ = "game_casts"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("game_sessions.id"), nullable=False)
    character_id = Column(String, ForeignKey("script_characters.id"), nullable=False)
    actor_type = Column(String, nullable=False)
    actor_id = Column(String, nullable=False)
    agent_id = Column(String, default="")
    user_id = Column(String, default="")
    role_name = Column(String, default="")
    is_player = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    session = relationship("GameSession", back_populates="casts")