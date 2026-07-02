# -*- coding: utf-8 -*-
"""Internal implementation."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.db.base import get_db
from api.core.responses import success_response, error_response
from api.repositories.agent_repository import AgentRepository
from api.services.agent_runtime_service import AgentRuntimeService

router = APIRouter(prefix="/agents", tags=["Agent"])


@router.get("/")
def get_agents(db: Session = Depends(get_db)):
    """Internal implementation."""
    try:
        repo = AgentRepository(db)
        agents = repo.get_all()
        return success_response({"agents": agents})
    except Exception as e:
        return error_response(code="FETCH_FAILED", message=str(e))


@router.post("/")
def create_agent(data: dict, db: Session = Depends(get_db)):
    """Internal implementation."""
    try:
        from api.models.agent import Agent
        from datetime import datetime, timezone
        import uuid
        repo = AgentRepository(db)
        agent = Agent(
            id=data.get("id") or f"agent_{uuid.uuid4().hex[:8]}",
            name=data.get("name", ""),
            role=data.get("role", ""),
            model=data.get("model", ""),
            persona_id=data.get("persona_id", ""),
            status=data.get("status", "active"),
            domains=data.get("domains", []),
            identity_doc=data.get("identity_doc", ""),
            constitution=data.get("constitution", ""),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        agent = repo.create(agent)
        return success_response(agent)
    except Exception as e:
        return error_response(code="CREATE_FAILED", message=str(e))


@router.get("/{agent_id}")
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Internal implementation."""
    repo = AgentRepository(db)
    agent = repo.get_by_id(agent_id)
    if not agent:
        return error_response(code="NOT_FOUND", message="Not found", status_code=404)
    return success_response(agent)


@router.get("/{agent_id}/state")
def get_agent_state(agent_id: str, session_id: str = None, db: Session = Depends(get_db)):
    """Internal implementation."""
