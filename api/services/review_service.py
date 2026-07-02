import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from api.models.review import ReviewReport
from api.repositories.review_repository import ReviewRepository


def utc_now():
    return datetime.now(timezone.utc)


class ReviewService:
    def __init__(self, db: Session):
        self.repo = ReviewRepository(db)

    def run_review(self, session_id: str, generated_by: str = "system") -> dict:
        review = self.repo.get_by_session(session_id)
        if review is None:
            review = ReviewReport(
                id=f"review_{uuid.uuid4().hex[:8]}",
                session_id=session_id,
                status="pending",
                generated_by=generated_by,
                created_at=utc_now(),
                updated_at=utc_now(),
            )
            review = self.repo.create(review)
        review.status = "generating"
        review.updated_at = utc_now()
        self.repo.update(review)
        return {"status": "generating", "session_id": session_id, "review_id": review.id}

    def get_review(self, session_id: str) -> ReviewReport | None:
        return self.repo.get_by_session(session_id)