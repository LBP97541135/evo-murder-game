"""
EvoMap Murder Game - Health Check Routes
"""

from fastapi import APIRouter
from api.main import orchestrator

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "agents_registered": len(orchestrator.agents),
        "active_sessions": len(orchestrator.sessions),
    }
