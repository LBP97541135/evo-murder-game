"""
EvoMap Murder Game - Memory & Evolution Routes

经验记录、经验召回、记忆状态查询。
"""

from fastapi import APIRouter, HTTPException

from api.schemas.invoke_types import MemoryRecordRequest, MemoryRecallRequest
from api.orchestrator import orchestrator

router = APIRouter()


@router.post("/record")
async def record_memory(req: MemoryRecordRequest):
    """记录 Agent 经验到 EvoMap 私有记忆库。"""
    agent = None
    for a in orchestrator.agents.values():
        if a.node_id == req.node_id:
            agent = a
            break
    if not agent or not agent.registered:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent.record_experience(
        signals=req.signals, gene_id=req.gene_id,
        status=req.status, score=req.score, summary=req.summary,
    )


@router.post("/recall")
async def recall_memory(req: MemoryRecallRequest):
    """召回 Agent 历史经验。"""
    agent = None
    for a in orchestrator.agents.values():
        if a.node_id == req.node_id:
            agent = a
            break
    if not agent or not agent.registered:
        raise HTTPException(status_code=404, detail="Agent not found")

    return agent.recall_experience(signals=req.signals, limit=req.limit)


@router.get("/status/{agent_key}")
async def memory_status(agent_key: str):
    """查看 Agent 记忆概况。"""
    agent = orchestrator.agents.get(agent_key)
    if not agent or not agent.registered:
        raise HTTPException(status_code=404, detail="Agent not found or not registered")
    return agent.client.memory_status()
