import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from api.models.session import GameCast
from api.repositories.session_repository import SessionRepository


def utc_now():
    return datetime.now(timezone.utc)


class CastingService:
    def __init__(self, db: Session):
        self.repo = SessionRepository(db)

    def cast_session(self, session_id: str, casts_data: list[dict]) -> list[GameCast]:
        casts = []
        for data in casts_data:
            cast = GameCast(
                id=f"cast_{uuid.uuid4().hex[:8]}",
                session_id=session_id,
                character_id=data.get("character_id", ""),
                actor_type=data.get("actor_type", data.get("type", "agent")),
                actor_id=data.get("actor_id", data.get("agentKey", "")),
                agent_id=data.get("agent_id", data.get("agentKey", "")),
                user_id=data.get("user_id", ""),
                role_name=data.get("role_name", data.get("role", "")),
                is_player=bool(data.get("is_player", False)),
                created_at=utc_now(),
                updated_at=utc_now(),
            )
            casts.append(self.repo.create_cast(cast))
        return casts

    def get_casts(self, session_id: str) -> list[GameCast]:
        return self.repo.get_casts(session_id)

    def reset_casts(self, session_id: str) -> bool:
        return self.repo.delete_casts_by_session(session_id)