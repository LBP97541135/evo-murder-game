import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from api.models.agent import AgentRuntimeState
from api.repositories.agent_repository import AgentRepository


def utc_now():
    return datetime.now(timezone.utc)


class AgentRuntimeService:
    def __init__(self, db: Session):
        self.repo = AgentRepository(db)

    def get_state(self, session_id: str, agent_id: str) -> AgentRuntimeState | None:
        return self.repo.get_runtime_state(session_id, agent_id)

    def create_state(self, session_id: str, agent_id: str, character_id: str = "", phase: str = "") -> AgentRuntimeState:
        state = AgentRuntimeState(
            id=f"state_{uuid.uuid4().hex[:8]}",
            session_id=session_id,
            agent_id=agent_id,
            character_id=character_id,
            phase=phase,
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        return self.repo.create_runtime_state(state)

    def update_state(self, state: AgentRuntimeState) -> AgentRuntimeState:
        state.updated_at = utc_now()
        return self.repo.update_runtime_state(state)

    def list_states(self, session_id: str) -> list[AgentRuntimeState]:
        return self.repo.get_runtime_states(session_id)