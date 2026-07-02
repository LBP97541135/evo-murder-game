from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, String, Text, Integer, Float, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from api.db.base import Base


def utc_now():
    return datetime.now(timezone.utc)


class Script(Base):
    __tablename__ = "scripts"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    author = Column(String, default="")
    version = Column(String, default="1.0.0")
    genre = Column(String, default="")
    theme = Column(String, default="")
    difficulty = Column(String, default="medium")
    duration_minutes = Column(Integer, default=120)
    player_count = Column(Integer, default=6)
    emotion_level = Column(Float, default=0.0)
    inference_level = Column(Float, default=0.0)
    horror_level = Column(Float, default=0.0)
    cover_image = Column(Text, default="")
    source_type = Column(String, default="manual")
    status = Column(String, default="active")
    metadata_json = Column(JSON, default={})
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    characters = relationship("ScriptCharacter", back_populates="script", cascade="all, delete-orphan")
    truths = relationship("ScriptTruth", back_populates="script", uselist=False, cascade="all, delete-orphan")


class ScriptCharacter(Base):
    __tablename__ = "script_characters"

    id = Column(String, primary_key=True)
    script_id = Column(String, ForeignKey("scripts.id"), nullable=False)
    name = Column(String, nullable=False)
    bio = Column(Text, default="")
    personality = Column(Text, default="")
    public_context = Column(Text, default="")
    private_secret = Column(Text, default="")
    behavior_rules = Column(Text, default="")
    role_type = Column(String, default="suspect")
    is_victim = Column(Boolean, default=False)
    is_killer = Column(Boolean, default=False)
    is_player_candidate = Column(Boolean, default=True)
    avatar_image = Column(Text, default="")
    background_image = Column(Text, default="")
    order_index = Column(Integer, default=0)
    metadata_json = Column(JSON, default={})
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    script = relationship("Script", back_populates="characters")


class ScriptTruth(Base):
    __tablename__ = "script_truths"

    id = Column(String, primary_key=True)
    script_id = Column(String, ForeignKey("scripts.id"), nullable=False, unique=True)
    global_story = Column(Text, default="")
    truth_summary = Column(Text, default="")
    killer_character_id = Column(String, default="")
    motive = Column(Text, default="")
    method = Column(Text, default="")
    timeline = Column(Text, default="")
    reveal_text = Column(Text, default="")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    script = relationship("Script", back_populates="truths")