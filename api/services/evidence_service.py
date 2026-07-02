import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from api.models.evidence import EvidenceInstance
from api.repositories.evidence_repository import EvidenceRepository


def utc_now():
    return datetime.now(timezone.utc)


class EvidenceService:
    def __init__(self, db: Session):
        self.repo = EvidenceRepository(db)

    def get_evidences(self, session_id: str) -> list[EvidenceInstance]:
        return self.repo.get_by_session(session_id)

    def discover_evidence(self, session_id: str, evidence_id: str, discovery_state: str = "discovered") -> EvidenceInstance:
        evidence = self.repo.get_by_id(evidence_id)
        if not evidence:
            raise ValueError("Evidence not found")
        if evidence.session_id != session_id:
            raise ValueError("Evidence does not belong to session")
        evidence.discovery_state = discovery_state
        evidence.updated_at = utc_now()
        return self.repo.update(evidence)

    def present_evidence(self, session_id: str, evidence_id: str, target_character_id: str = "", is_public: bool = True) -> EvidenceInstance:
        evidence = self.repo.get_by_id(evidence_id)
        if not evidence:
            raise ValueError("Evidence not found")
        if evidence.session_id != session_id:
            raise ValueError("Evidence does not belong to session")
        evidence.visibility = "public" if is_public else "private"
        evidence.is_public = is_public
        metadata = evidence.metadata_json or {}
        metadata.setdefault("presentations", []).append({
            "target_character_id": target_character_id,
            "is_public": is_public,
            "presented_at": utc_now().isoformat(),
        })
        evidence.metadata_json = metadata
        evidence.updated_at = utc_now()
        return self.repo.update(evidence)

    def get_public_evidences(self, session_id: str) -> list[EvidenceInstance]:
        return self.repo.get_public_by_session(session_id)

    def create_from_script(self, session_id: str, script_id: str) -> list[EvidenceInstance]:
        return self.repo.create_from_script(session_id, script_id)