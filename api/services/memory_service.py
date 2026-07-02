from datetime import datetime, timezone
from sqlalchemy.orm import Session
from api.repositories.agent_repository import AgentRepository


def utc_now():
    return datetime.now(timezone.utc)


class MemoryService:
    def __init__(self, db: Session):
        self.repo = AgentRepository(db)

    def add_short_memory(self, session_id: str, agent_id: str, content: str) -> bool:
        state = self.repo.get_runtime_state(session_id, agent_id)
        if not state:
            return False
        memories = list(state.short_memory or [])
        memories.append({"content": content, "timestamp": utc_now().isoformat()})
        state.short_memory = memories
        state.updated_at = utc_now()
        self.repo.save_runtime_state(state)
        return True

    def get_short_memory(self, session_id: str, agent_id: str) -> list:
        state = self.repo.get_runtime_state(session_id, agent_id)
        return list(state.short_memory or []) if state else []

    def update_summary(self, session_id: str, agent_id: str, summary: str) -> bool:
        state = self.repo.get_runtime_state(session_id, agent_id)
        if not state:
            return False
        state.compressed_summary = summary
        state.updated_at = utc_now()
        self.repo.save_runtime_state(state)
        return True