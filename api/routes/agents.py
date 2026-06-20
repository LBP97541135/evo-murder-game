"""
EvoMap Murder Game - Agent Management Routes

Agent 注册、列表、心跳、进化更新、人设管理。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from api.schemas.invoke_types import (
    AgentRegistrationRequest, AgentRegistrationResponse,
    EvolutionUpdateRequest,
)
from api.agents.agent_orchestrator import AgentNode, AgentRole
from api.agents.agent_persona_service import (
    get_all_personas, get_persona_by_key, match_personas_for_script,
    init_preset_personas,
)
from api.orchestrator import orchestrator

router = APIRouter()


# ============================
# 人设相关请求模型
# ============================

class PersonaLoadRequest(BaseModel):
    """加载人设到 Agent 的请求。"""
    agent_key: str          # Agent 在编排器中的 key
    persona_key: str        # 人设库中的 key


class PersonaMatchRequest(BaseModel):
    """自动匹配人设的请求。"""
    script_genre: str = ""  # 剧本类型：推理本/情感本/阵营本/机制本
    difficulty: str = ""    # 难度：easy/medium/hard


# ============================
# Agent CRUD
# ============================

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

    # 持久化到数据库
    orchestrator._save_agent_to_db(agent, key)

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
            "persona_key": agent.persona_key or "",
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

    # 持久化更新到数据库
    orchestrator._save_agent_to_db(agent, agent_key)

    return {
        "agent_key": agent_key,
        "update_type": req.update_type,
        "new_content": req.new_content,
        "status": "updated",
    }


# ============================
# 人设管理
# ============================

@router.post("/personas/init")
async def init_personas():
    """初始化预设人设到数据库（幂等）。"""
    result = init_preset_personas()
    return result


@router.get("/personas")
async def list_personas(role: Optional[str] = None):
    """获取人设列表，可按角色筛选（companion/dm/assistant）。"""
    personas = get_all_personas(role=role)
    return {"personas": personas, "total": len(personas)}


@router.get("/personas/{persona_key}")
async def get_persona_detail(persona_key: str):
    """获取人设详情。"""
    persona = get_persona_by_key(persona_key)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")
    return persona


@router.post("/personas/load")
async def load_persona(req: PersonaLoadRequest):
    """加载指定人设到 Agent，融合 constitution 和 identity_doc。"""
    result = orchestrator.load_persona_to_agent(req.agent_key, req.persona_key)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/personas/auto-match")
async def auto_match_personas(req: PersonaMatchRequest):
    """根据剧本类型和难度，为所有 Agent 自动匹配最合适的人设。"""
    result = orchestrator.auto_match_personas(
        script_genre=req.script_genre,
        difficulty=req.difficulty,
    )
    return result
