import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from api.models.review import Skill, SkillUsageLog, ExperienceRecord
from api.repositories.skill_repository import SkillRepository


def utc_now():
    return datetime.now(timezone.utc)


class SkillService:
    def __init__(self, db: Session):
        self.repo = SkillRepository(db)

    def create_skill(self, data: dict) -> Skill:
        skill = Skill(
            id=data.get("id") or f"skill_{uuid.uuid4().hex[:8]}",
            name=data.get("name", ""),
            version=data.get("version", "1.0.0"),
            type=data.get("type", "prompt_skill"),
            category=data.get("category", ""),
            applicable_roles=data.get("applicable_roles", []),
            signals=data.get("signals", []),
            description=data.get("description", ""),
            prompt_content=data.get("prompt_content", ""),
            strategy=data.get("strategy", ""),
            examples=data.get("examples", ""),
            anti_patterns=data.get("anti_patterns", ""),
            source_type=data.get("source_type", "manual"),
            source_experience_id=data.get("source_experience_id", ""),
            source_session_id=data.get("source_session_id", ""),
            source_script_id=data.get("source_script_id", ""),
            created_by_agent_id=data.get("created_by_agent_id", ""),
            injection_mode=data.get("injection_mode", "append_system_prompt"),
            injection_priority=data.get("injection_priority", 50),
            max_tokens=data.get("max_tokens", 800),
            status=data.get("status", "active"),
            created_at=utc_now(),
            updated_at=utc_now(),
            metadata_json=data.get("metadata", data.get("metadata_json", {})),
        )
        return self.repo.create(skill)

    def get_skill(self, skill_id: str) -> Skill | None:
        return self.repo.get_by_id(skill_id)

    def list_skills(self, category: str = None, status: str = None) -> list:
        return self.repo.list(category=category, status=status)

    def search_skills(self, role: str = None, category: str = None, signals: list = None, limit: int = 10) -> list:
        return self.repo.search(role=role, category=category, signals=signals, limit=limit)

    def update_skill(self, skill_id: str, data: dict) -> Skill:
        skill = self.repo.get_by_id(skill_id)
        if not skill:
            raise ValueError("不存在")
        for key, value in data.items():
            if hasattr(skill, key) and key != "id":
                setattr(skill, key, value)
        skill.updated_at = utc_now()
        return self.repo.update(skill)

    def delete_skill(self, skill_id: str) -> bool:
        return self.repo.delete(skill_id)

    def inject_skills(self, session_id: str, agent_id: str, role: str, phase: str) -> str:
        skills = self.repo.search(role=role, limit=10)
        return "\n\n".join(skill.prompt_content for skill in skills if getattr(skill, "prompt_content", ""))

    def record_usage(self, skill_id: str, session_id: str, agent_id: str, phase: str, tokens: int) -> SkillUsageLog:
        log = SkillUsageLog(
            id=f"log_{uuid.uuid4().hex[:8]}",
            skill_id=skill_id,
            session_id=session_id,
            agent_id=agent_id,
            phase=phase,
            injection_tokens=tokens,
            created_at=utc_now(),
        )
        return self.repo.create_usage_log(log)

    def create_experience(self, data: dict) -> ExperienceRecord:
        record = ExperienceRecord(
            id=data.get("id") or f"exp_{uuid.uuid4().hex[:8]}",
            session_id=data.get("session_id", ""),
            script_id=data.get("script_id", ""),
            agent_id=data.get("agent_id", ""),
            role=data.get("role", ""),
            category=data.get("category", ""),
            signals=data.get("signals", []),
            status=data.get("status", "success"),
            self_score=data.get("self_score", 0.0),
            summary=data.get("summary", ""),
            detail=data.get("detail", ""),
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        return self.repo.create_experience(record)

    def get_experiences(self, session_id: str = None) -> list:
        return self.repo.get_experiences(session_id=session_id)

    def generate_skill_from_experience(self, experience_id: str) -> Skill:
        experience = self.repo.get_experience(experience_id)
        if not experience:
            raise ValueError("不存在")
        return self.create_skill({
            "name": f"Skill from experience: {str(experience.summary)[:20]}",
            "type": "prompt_skill",
            "category": experience.category,
            "applicable_roles": [experience.role] if experience.role else [],
            "signals": experience.signals or [],
            "description": experience.summary,
            "prompt_content": experience.detail,
            "source_type": "experience",
            "source_experience_id": experience_id,
            "source_session_id": experience.session_id,
            "source_script_id": experience.script_id,
            "status": "draft",
        })

    def export_skill(self, skill_id: str) -> dict:
        skill = self.repo.get_by_id(skill_id)
        if not skill:
            raise ValueError("不存在")
        return {
            "id": skill.id,
            "name": skill.name,
            "version": skill.version,
            "type": skill.type,
            "category": skill.category,
            "applicable_roles": skill.applicable_roles,
            "signals": skill.signals,
            "description": skill.description,
            "prompt_content": skill.prompt_content,
            "strategy": skill.strategy,
            "examples": skill.examples,
            "anti_patterns": skill.anti_patterns,
            "injection_mode": skill.injection_mode,
            "injection_priority": skill.injection_priority,
            "max_tokens": skill.max_tokens,
            "metadata": skill.metadata_json,
        }

    def import_skill(self, data: dict) -> Skill:
        return self.create_skill(data)