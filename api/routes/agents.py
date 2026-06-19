"""
EvoMap Murder Game - Agent Management Routes

Agent 注册、列表、心跳、进化更新。
"""

from fastapi import APIRouter, HTTPException

from api.schemas.invoke_types import (
    AgentRegistrationRequest, AgentRegistrationResponse,
    EvolutionUpdateRequest,
)
from api.agents.agent_orchestrator import AgentNode, AgentRole
from api.orchestrator import orchestrator

router = APIRouter()


@router.post("/register", response_model=AgentRegistrationResponse)
async def register_agent(req: AgentRegistrationRequest):
    """注册一个新 Agent 到系统（同时尝试注册到 EvoMap 网络，失败则降级为本地模式）。"""
    role = AgentRole(req.role)
    agent = AgentNode(
        role=role,
        name=req.name,
        model=req.model,
        identity_doc=req.identity_doc,
        constitution=req.constitution,
    )
    key = orchestrator.add_agent(agent)
    result = agent.register()

    # 无论 EvoMap 是否成功，都返回注册结果
    mode = result.get("mode", "evomap")
    warning = result.get("warning", "")

    return AgentRegistrationResponse(
        node_id=agent.node_id or "",
        node_secret=agent.node_secret or "",
        claim_url=result.get("claim_url", ""),
        claim_code=result.get("claim_code", ""),
        status="local" if mode == "local" else "alive",
        mode=mode,
        warning=warning,
    )


@router.get("/list")
async def list_agents():
    """列出所有已注册的 Agent。"""
    agents = []
    for key, agent in orchestrator.agents.items():
        agents.append({
            "key": key,
            "name": agent.name,
            "role": agent.role.value,
            "node_id": agent.node_id or "",
            "registered": agent.registered,
            "model": agent.model,
        })
    return {"agents": agents}


@router.post("/heartbeat/{agent_key}")
async def agent_heartbeat(agent_key: str):
    """发送心跳保活。"""
    agent = orchestrator.agents.get(agent_key)
    if not agent or not agent.registered:
        raise HTTPException(status_code=404, detail="Agent not found or not registered")
    return agent.heartbeat()


@router.post("/evolve/{agent_key}")
async def evolve_agent(agent_key: str, req: EvolutionUpdateRequest):
    """更新 Agent 的 constitution 或 identity_doc（进化核心操作）。"""
    agent = orchestrator.agents.get(agent_key)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    if req.update_type == "constitution":
        agent.update_constitution(req.new_content)
    elif req.update_type == "identity_doc":
        agent.update_identity(req.new_content)
    else:
        raise HTTPException(status_code=400, detail="Invalid update_type")

    return {
        "agent_key": agent_key,
        "update_type": req.update_type,
        "new_content": req.new_content,
        "status": "updated",
    }
