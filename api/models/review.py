from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, String, Text, Integer, Float, JSON, DateTime
from api.db.base import Base


def utc_now():
    return datetime.now(timezone.utc)


class ReviewReport(Base):
    __tablename__ = "review_reports"

    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False)
    status = Column(String, default="pending")
    truth_summary = Column(Text, default="")
    player_result_json = Column(JSON, default={})
    key_clues_json = Column(JSON, default=[])
    timeline_json = Column(JSON, default=[])
    report_content = Column(Text, default="")
    generated_by = Column(String, default="")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    metadata_json = Column(JSON, default={})


class ExperienceRecord(Base):
    __tablename__ = "experience_records"

    id = Column(String, primary_key=True)
    session_id = Column(String, default="")
    script_id = Column(String, default="")
    agent_id = Column(String, default="")
    role = Column(String, default="")
    category = Column(String, default="")
    signals = Column(JSON, default=[])
    status = Column(String, default="success")
    self_score = Column(Float, default=0.0)
    summary = Column(Text, default="")
    detail = Column(Text, default="")
    dm_reviewed = Column(Boolean, default=False)
    dm_score = Column(Float, default=0.0)
    dm_comment = Column(Text, default="")
    dm_suggestions = Column(Text, default="")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    metadata_json = Column(JSON, default={})


class Skill(Base):
    __tablename__ = "skills"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    version = Column(String, default="1.0.0")
    type = Column(String, default="prompt_skill")
    category = Column(String, default="")
    applicable_roles = Column(JSON, default=[])
    signals = Column(JSON, default=[])
    description = Column(Text, default="")
    prompt_content = Column(Text, default="")
    strategy = Column(Text, default="")
    examples = Column(Text, default="")
    anti_patterns = Column(Text, default="")
    source_type = Column(String, default="manual")
    source_experience_id = Column(String, default="")
    source_session_id = Column(String, default="")
    source_script_id = Column(String, default="")
    created_by_agent_id = Column(String, default="")
    quality_score = Column(Float, default=0.0)
    effectiveness_score = Column(Float, default=0.0)
    review_status = Column(String, default="draft")
    reviewed_by = Column(String, default="")
    review_comment = Column(Text, default="")
    injection_mode = Column(String, default="append_system_prompt")
    injection_priority = Column(Integer, default=50)
    max_tokens = Column(Integer, default=800)
    usage_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    last_used_at = Column(DateTime)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    metadata_json = Column(JSON, default={})


class SkillUsageLog(Base):
    __tablename__ = "skill_usage_logs"

    id = Column(String, primary_key=True)
    skill_id = Column(String, nullable=False)
    session_id = Column(String, default="")
    agent_id = Column(String, default="")
    phase = Column(String, default="")
    injection_tokens = Column(Integer, default=0)
    result_quality = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utc_now)
    metadata_json = Column(JSON, default={})