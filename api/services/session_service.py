import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from api.models.session import GameSession
from api.repositories.session_repository import SessionRepository


def utc_now():
    return datetime.now(timezone.utc)


class SessionService:
    def __init__(self, db: Session):
        self.repo = SessionRepository(db)

    def create_session(self, data: dict) -> GameSession:
        session = GameSession(
            id=f"session_{uuid.uuid4().hex[:8]}",
            script_id=data.get("script_id", ""),
            host_user_id=data.get("host_user_id", ""),
            title=data.get("title", ""),
            current_phase=data.get("current_phase", "setup"),
            status=data.get("status", "active"),
            player_character_id=data.get("player_character_id", ""),
            dm_agent_id=data.get("dm_agent_id", ""),
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        return self.repo.create(session)

    def get_session(self, session_id: str) -> GameSession | None:
        return self.repo.get_by_id(session_id)

    def list_sessions(self, status: str = None) -> list:
        return self.repo.get_all_sessions(status=status)

    def end_session(self, session_id: str) -> GameSession | None:
        session = self.repo.get_by_id(session_id)
        if not session:
            return None
        session.status = "ended"
        session.ended_at = utc_now()
        session.updated_at = utc_now()
        return self.repo.update(session)

    def get_snapshot(self, session_id: str) -> dict | None:
        session = self.repo.get_by_id(session_id)
        if not session:
            return None
        return {
            "session": session,
            "phase_events": self.repo.get_phase_events(session_id),
            "casts": self.repo.get_casts(session_id),
        }