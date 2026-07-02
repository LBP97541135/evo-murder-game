from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from api.db.base import Base


def utc_now():
    return datetime.now(timezone.utc)


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    model = Column(String, default="")
    persona_id = Column(String, default="")
    status = Column(String, default="active")
    domains = Column(JSON, default=[])
    identity_doc = Column(Text, default="")
    constitution = Column(Text, default="")
    external_provider = Column(String, default="")
    external_ref = Column(String, default="")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    metadata_json = Column(JSON, default={})

    runtime_states = relationship("AgentRuntimeState", back_populates="agent", cascade="all, delete-orphan")


class AgentRuntimeState(Base):
    __tablename__ = "agent_runtime_states"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("game_sessions.id"), nullable=False)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    character_id = Column(String, default="")
    phase = Column(String, default="")
    short_memory = Column(JSON, default=[])
    compressed_summary = Column(Text, default="")
    key_facts = Column(JSON, default=[])
    known_evidence_ids = Column(JSON, default=[])
    loaded_skill_ids = Column(JSON, default=[])
    intent_json = Column(JSON, default={})
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    agent = relationship("Agent", back_populates="runtime_states")