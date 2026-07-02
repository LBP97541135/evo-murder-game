import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from api.models.session import GamePhaseEvent
from api.repositories.session_repository import SessionRepository

PHASE_ORDER = ["setup", "intro", "investigation", "discussion", "voting", "reveal", "review"]


def utc_now():
    return datetime.now(timezone.utc)


class PhaseService:
    def __init__(self, db: Session):
        self.repo = SessionRepository(db)

    def get_current_phase(self, session_id: str) -> str | None:
        session = self.repo.get_by_id(session_id)
        return session.current_phase if session else None

    def advance_phase(self, session_id: str) -> dict:
        session = self.repo.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found")
        current = session.current_phase or "setup"
        if current not in PHASE_ORDER or current == PHASE_ORDER[-1]:
            raise ValueError("Cannot advance phase")
        next_phase = PHASE_ORDER[PHASE_ORDER.index(current) + 1]
        return self.force_phase(session_id, next_phase, "advance", from_phase=current)

    def force_phase(self, session_id: str, phase: str, reason: str = "force", from_phase: str | None = None) -> dict:
        session = self.repo.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found")
        previous = from_phase if from_phase is not None else (session.current_phase or "")
        session.current_phase = phase
        session.updated_at = utc_now()
        self.repo.update(session)
        event = GamePhaseEvent(
            id=f"phase_{uuid.uuid4().hex[:8]}",
            session_id=session_id,
            from_phase=previous,
            to_phase=phase,
            reason=reason,
            triggered_by="system",
            created_at=utc_now(),
        )
        self.repo.create_phase_event(event)
        return {"event_id": event.id, "from_phase": previous, "to_phase": phase, "reason": reason}