from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Float, JSON, DateTime
from api.db.base import Base


def utc_now():
    return datetime.now(timezone.utc)


class AgentPersona(Base):
    __tablename__ = "agent_personas"

    id = Column(String, primary_key=True)
    key = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    vibe = Column(Text, default="")
    style = Column(Text, default="")
    genius = Column(JSON, default=[])
    personality = Column(JSON, default=[])
    script_types = Column(JSON, default=[])
    active_level = Column(String, default="medium")
    pace = Column(String, default="medium")
    strengths = Column(JSON, default=[])
    prompt_style = Column(Text, default="")
    fairness = Column(Text, default="")
    persona_text = Column(Text, default="")
    backstory = Column(Text, default="")
    speech_style = Column(Text, default="")
    values = Column(JSON, default=[])
    anti_patterns = Column(JSON, default=[])
    role_match = Column(Text, default="")
    reason = Column(Text, default="")
    rating = Column(Float, default=4.5)
    history_count = Column(Integer, default=0)
    recent_tags = Column(JSON, default=[])
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)