from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.db.base import get_db
from api.core.responses import success_response, error_response
from api.services.session_service import SessionService
from api.schemas.session import GameSessionResponse, GamePhaseEventResponse, GameCastResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


def utc_now():
    return datetime.now(timezone.utc)


@router.post("/")
def create_session(data: dict, db: Session = Depends(get_db)):
    try:
        service = SessionService(db)
        session = service.create_session(data)
        return success_response(GameSessionResponse.model_validate(session))
    except Exception as e:
        return error_response(code="CREATE_FAILED", message=str(e))


@router.get("/{session_id}")
def get_session(session_id: str, db: Session = Depends(get_db)):
    service = SessionService(db)
    session = service.get_session(session_id)
    if not session:
        return error_response(code="NOT_FOUND", message="Not found", status_code=404)
    return success_response(GameSessionResponse.model_validate(session))


@router.get("/{session_id}/snapshot")
def get_session_snapshot(session_id: str, db: Session = Depends(get_db)):
    service = SessionService(db)
    snapshot = service.get_snapshot(session_id)
    if not snapshot:
        return error_response(code="NOT_FOUND", message="Not found", status_code=404)
    return success_response({
        "session": GameSessionResponse.model_validate(snapshot["session"]),
        "phase_events": [GamePhaseEventResponse.model_validate(e) for e in snapshot["phase_events"]],
        "casts": [GameCastResponse.model_validate(c) for c in snapshot["casts"]],
    })


@router.post("/{session_id}/vote")
def submit_vote(session_id: str, data: dict, db: Session = Depends(get_db)):
    try:
        voter_id = data.get("voter_id")
        target_id = data.get("target_id")
        if not voter_id or not target_id:
            return error_response(code="MISSING_PARAM", message="Missing voter_id or target_id")
        service = SessionService(db)
        session = service.get_session(session_id)
        if not session:
            return error_response(code="NOT_FOUND", message="Not found", status_code=404)
        metadata = session.metadata_json or {}
        votes = metadata.get("votes", [])
        votes.append({"voter_id": voter_id, "target_id": target_id, "timestamp": utc_now().isoformat()})
        metadata["votes"] = votes
        session.metadata_json = metadata
        session.updated_at = utc_now()
        from api.repositories.session_repository import SessionRepository
        SessionRepository(db).update(session)
        return success_response({"message": "Vote submitted", "session_id": session_id})
    except Exception as e:
        return error_response(code="VOTE_FAILED", message=str(e))


@router.post("/{session_id}/reveal")
def reveal_truth(session_id: str, db: Session = Depends(get_db)):
    try:
        service = SessionService(db)
        session = service.get_session(session_id)
        if not session:
            return error_response(code="NOT_FOUND", message="Not found", status_code=404)
        from api.services.phase_service import PhaseService
        result = PhaseService(db).force_phase(session_id, "reveal", "truth_revealed")
        return success_response({"message": "Truth revealed", "session_id": session_id, "phase": result["to_phase"]})
    except Exception as e:
        return error_response(code="REVEAL_FAILED", message=str(e))


@router.post("/{session_id}/end")
def end_session(session_id: str, db: Session = Depends(get_db)):
    service = SessionService(db)
    session = service.end_session(session_id)
    if not session:
        return error_response(code="NOT_FOUND", message="Not found", status_code=404)
    return success_response({"message": "Game ended", "session_id": session_id})