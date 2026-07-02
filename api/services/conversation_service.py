import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from api.models.conversation import ConversationThread, ConversationMessage
from api.repositories.conversation_repository import ConversationRepository


def utc_now():
    return datetime.now(timezone.utc)


class ConversationService:
    def __init__(self, db: Session):
        self.repo = ConversationRepository(db)

    def create_thread(self, session_id: str, thread_type: str = "public", participant_ids: list[str] | None = None, title: str = "") -> ConversationThread:
        thread = ConversationThread(
            id=f"thread_{uuid.uuid4().hex[:8]}",
            session_id=session_id,
            thread_type=thread_type,
            title=title,
            participant_ids=participant_ids or [],
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        return self.repo.create_thread(thread)

    def send_message(self, session_id: str, thread_id: str, sender_type: str, sender_id: str = "", sender_name: str = "", content: str = "", **kwargs) -> ConversationMessage:
        message = ConversationMessage(
            id=f"msg_{uuid.uuid4().hex[:8]}",
            session_id=session_id,
            thread_id=thread_id,
            sender_type=sender_type,
            sender_id=sender_id,
            sender_name=sender_name,
            target_id=kwargs.get("target_id", ""),
            message_type=kwargs.get("message_type", "text"),
            content=content,
            visibility=kwargs.get("visibility", "public"),
            phase=kwargs.get("phase", ""),
            created_at=utc_now(),
        )
        return self.repo.create_message(message)

    def get_messages(self, session_id: str, thread_id: str | None = None, limit: int = 50) -> list:
        return self.repo.get_messages(session_id, thread_id=thread_id, limit=limit)

    def get_threads(self, session_id: str, thread_type: str | None = None) -> list:
        return self.repo.get_threads(session_id, thread_type=thread_type)