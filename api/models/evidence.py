from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, String, Text, Integer, JSON, DateTime, ForeignKey
from api.db.base import Base


def utc_now():
    return datetime.now(timezone.utc)


class EvidenceInstance(Base):
    __tablename__ = "evidence_instances"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("game_sessions.id"), nullable=False)
    script_id = Column(String, ForeignKey("scripts.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, default="")
    importance = Column(String, default="medium")
    basic_description = Column(Text, default="")
    detailed_description = Column(Text, default="")
    deep_description = Column(Text, default="")
    discovery_state = Column(String, default="hidden")
    visibility = Column(String, default="private")
    owner_character_id = Column(String, default="")
    is_public = Column(Boolean, default=False)
    image_path = Column(Text, default="")
    unlock_level = Column(Integer, default=1)
    related_character_ids = Column(JSON, default=[])
    related_evidence_ids = Column(JSON, default=[])
    combinable_with_ids = Column(JSON, default=[])
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    metadata_json = Column(JSON, default={})