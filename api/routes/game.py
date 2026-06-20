"""
EvoMap Murder Game - Game Session Routes

游戏 Session 创建、阶段管理、广播、投票、复盘。
v2.1 新增：Agent 游戏状态、意图系统、记忆压缩。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from api.schemas.invoke_types import GameSessionRequest, GameSessionResponse
from api.agents.agent_orchestrator import AgentRole
from api.agents.game_engine import game_engine, GamePhase
from api.orchestrator import orchestrator

router = APIRouter()


# ============================
# 请求模型
# ============================

class VoteRequest(BaseModel):
    killer: str
    motive: str = ""
    voter: str = "player"


class PhaseForceRequest(BaseModel):
    phase: str


class AgentChatRequest(BaseModel):
    session_id: str
    agent_key: str
    content: str
    role: str = "agent"  # agent / player / dm


class ApproveIntentRequest(BaseModel):
    intent_type: str      # interject / private_chat / present_evidence
    approved: bool


class InterjectRequest(BaseModel):
    agent_key: str
    reason: str = ""


class PrivateMessageRequest(BaseModel):
    from_key: str         # 发送者 agent_key 或 "player"
    to_key: str           # 接收者 agent_key
    content: str


class ForceAnswerRequest(BaseModel):
    asker_key: str        # 提问者 agent_key 或 "player"
    target_key: str       # 被指定的 Agent key
    question: str


# ============================
# 游戏 Session
# ============================

@router.post("/create-session", response_model=GameSessionResponse)
async def create_game_session(req: GameSessionRequest):
    """创建游戏 Session，同时初始化游戏引擎和所有 Agent 游戏状态。"""
    if not orchestrator.agents:
        raise HTTPException(status_code=400, detail="No agents registered yet")

    result = orchestrator.create_game_session(
        topic=req.topic,
        script_name=req.script_id,
    )

    if "error" in result:
        raise HTTPException(status_code=500, detail=result)

    session_id = result.get("session_id", "")
    session_info = orchestrator.sessions.get(session_id, {})

    # 初始化游戏引擎（同时初始化 Agent 游戏状态 + 胶囊注入）
    game_engine.create_game(
        script_id=req.script_id,
        session_id=session_id,
        player_role_id=req.player_role_id,
    )

    return GameSessionResponse(
        session_id=session_id,
        participants=session_info.get("companions", []),
        status="active",
    )


# ============================
# 游戏阶段
# ============================

@router.get("/phase/{session_id}")
async def get_game_phase(session_id: str):
    """获取当前游戏阶段信息。"""
    info = game_engine.get_phase_info(session_id)
    if "error" in info:
        raise HTTPException(status_code=404, detail=info["error"])
    return info


@router.post("/phase/{session_id}/advance")
async def advance_game_phase(session_id: str):
    """推进到下一阶段，同时触发所有 Agent 的记忆压缩。"""
    result = game_engine.advance_phase(session_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


@router.post("/phase/{session_id}/force")
async def force_game_phase(session_id: str, req: PhaseForceRequest):
    """强制跳转到指定阶段（DM权限）。"""
    result = game_engine.force_phase(session_id, req.phase)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


# ============================
# 投票
# ============================

@router.post("/vote/{session_id}")
async def submit_vote(session_id: str, req: VoteRequest):
    """提交推理投票（凶手+动机）。"""
    result = game_engine.submit_vote(
        game_id=session_id,
        killer=req.killer,
        motive=req.motive,
        voter=req.voter,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


# ============================
# 消息广播
# ============================

@router.post("/broadcast/{session_id}")
async def broadcast_message(session_id: str, msg_type: str, payload: dict, from_role: str):
    """在游戏 Session 中广播消息。"""
    try:
        role = AgentRole(from_role)
    except ValueError:
        role = AgentRole.DM
    return orchestrator.broadcast_message(session_id, msg_type, payload, role)


# ============================
# 对话计数
# ============================

@router.post("/chat-count/{session_id}")
async def record_chat(session_id: str):
    """记录一次对话（用于阶段推进条件判断）。"""
    game_engine.record_chat(session_id)
    game = game_engine.get_game(session_id)
    return {
        "success": True,
        "chat_count": game.get("chat_count", 0) if game else 0,
        "can_advance": game_engine.can_advance(session_id),
    }


# ============================
# 复盘反思
# ============================

@router.post("/reflect/{session_id}")
async def post_game_reflection(session_id: str, game_result: dict):
    """游戏结束后，所有 Agent 执行自评并记录经验。"""
    return orchestrator.post_game_reflection(session_id, game_result)


# ============================
# 后剧情模式
# ============================

class PostGameRevealRequest(BaseModel):
    """后剧情请求——投票后的真相交代。"""
    killer: str = ""
    motive: str = ""
    voter: str = "player"
    correct: bool = False
    script_type: str = ""


@router.post("/reveal/{session_id}")
async def post_game_reveal(session_id: str, req: PostGameRevealRequest):
    """投票后执行后剧情——凶手交代 + DM 揭晓真相。

    自动调用 LLM 生成凶手交代和真相总结。
    """
    vote_result = {
        "killer": req.killer,
        "motive": req.motive,
        "voter": req.voter,
        "correct": req.correct,
        "script_type": req.script_type,
    }
    result = orchestrator.post_game_reveal(session_id, vote_result)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result)
    return result


@router.post("/reveal/{session_id}/spoiler")
async def generate_spoiler_story(session_id: str, req: PostGameRevealRequest):
    """投票后生成剧透故事——完整游戏剧情回顾。"""
    vote_result = {
        "killer": req.killer,
        "motive": req.motive,
        "voter": req.voter,
        "correct": req.correct,
    }
    result = orchestrator.generate_spoiler_story(session_id, vote_result)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result)
    return result


# ============================
# Agent 游戏状态
# ============================

@router.get("/agent-state/{session_id}/{agent_key}")
async def get_agent_state(session_id: str, agent_key: str):
    """获取指定 Agent 的完整游戏状态（记忆/角色/意图/证物）。"""
    state = game_engine.get_agent_state(session_id, agent_key)
    if not state:
        raise HTTPException(status_code=404, detail="Agent state not found")
    return {"success": True, "state": state}


# ============================
# 游戏会话完整信息（一站式接口）
# ============================

@router.get("/session-info/{session_id}")
async def get_session_info(session_id: str):
    """一站式获取本局游戏完整信息。

    返回：当前阶段、所有Agent与角色映射、证物统计、阶段历史。
    前端一次调用即可渲染游戏主界面。
    """
    # 阶段信息
    phase_info = game_engine.get_phase_info(session_id)
    if "error" in phase_info:
        raise HTTPException(status_code=404, detail=phase_info["error"])

    game = game_engine.get_game(session_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # 所有 Agent 的状态摘要（不含 secret）
    agents_info = []
    for key, agent_state in game.get("agents", {}).items():
        agents_info.append({
            "key": key,
            "name": agent_state.character.get("name", key),
            "role_type": agent_state.character.get("roleType", "unknown"),
            "is_killer": agent_state.character.get("isKiller", False),
            "is_victim": agent_state.character.get("isVictim", False),
            "image": agent_state.character.get("image", ""),
            "has_intents": any(v is not None for v in (agent_state.intents or {}).values()),
        })

    # 发言轮次信息（如果引擎支持）
    try:
        speak_round = game_engine.get_speak_round(session_id)
        if "error" in speak_round:
            speak_round = {"round_active": False}
    except Exception:
        speak_round = {"round_active": False}

    return {
        "success": True,
        "session_id": session_id,
        "phase": phase_info,
        "player": game.get("player_character"),
        "agents": agents_info,
        "speak_round": speak_round,
        "script_id": game.get("script_id", ""),
        "chat_count": game.get("chat_count", 0),
        "hints_used": game.get("hints_used", 0),
        "vote_result": game.get("vote_result"),
        "reveal_data": game.get("reveal_data"),   # 后剧情数据（REVEAL 阶段可用）
        "phase_history": game.get("phase_history", []),
        "started_at": game.get("started_at", ""),
    }


# ============================
# 玩家发言（一键封装）
# ============================

class PlayerChatRequest(BaseModel):
    content: str
    target_key: str = ""   # 如果为空则对所有人（DM模式）


@router.post("/chat/{session_id}")
async def player_chat(session_id: str, req: PlayerChatRequest):
    """玩家发言——自动拼装 invoke 请求并调用 LLM。

    - 如果 target_key 是某个 companion，自动注入该角色的 secret/violation
    - 如果 target_key 是 DM，以 DM 身份回复
    - 如果 target_key 为空，让 DM 以主持人身份回复
    - 自动记录 chat-count
    """
    game = game_engine.get_game(session_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # 确定目标 Agent 的游戏状态
    target_state = game.get("agents", {}).get(req.target_key) if req.target_key else None

    # 构建 Actor 信息
    if target_state and target_state.character:
        actor_data = {
            "id": target_state.character.get("id", req.target_key),
            "name": target_state.character.get("name", req.target_key),
            "bio": target_state.character.get("bio", ""),
            "personality": target_state.character.get("personality", ""),
            "context": target_state.character.get("context", ""),
            "secret": target_state.character.get("secret", ""),
            "violation": target_state.character.get("violation", ""),
            "role_type": target_state.character.get("roleType", "companion"),
        }
    else:
        # 没有指定 Agent 或目标没有角色 → 用 DM 回复
        actor_data = {
            "id": "dm", "name": "DM",
            "bio": "你是剧本杀主持人，掌握完整真相。",
            "personality": "专业沉稳，善于营造悬疑氛围。",
            "context": game.get("agents", {}).get("dm_DM-Persist", {}).character.get("context", ""),
            "secret": "", "violation": "", "role_type": "dm",
        }

    # 构建 invoke 请求
    from api.schemas.invoke_types import InvocationRequest, Actor, LLMMessage
    from api.llm.llm_service import invoke_with_pipeline, ROLE_SYSTEM_PROMPTS

    role = actor_data["role_type"]
    system_prompt = ROLE_SYSTEM_PROMPTS.get(role, ROLE_SYSTEM_PROMPTS["companion"])
    system_prompt += f"\n\n当前角色：{actor_data['name']}\n角色简介：{actor_data['bio']}\n性格：{actor_data['personality']}"

    if actor_data.get("secret"):
        system_prompt += f"\n角色秘密（仅你自己知道）：{actor_data['secret']}"
    if actor_data.get("violation"):
        system_prompt += f"\n行为限制（绝不能违反）：{actor_data['violation']}"

    result = invoke_with_pipeline(
        system_prompt=system_prompt,
        user_message=f"玩家对你说：{req.content}\n\n请以角色身份回复。",
        critique_prompt="",
        skip_critique=True,
    )

    final = result["final"]

    # 记录对话
    if req.target_key:
        game_engine.add_chat_to_agent(session_id, req.target_key, "player", req.content)
        game_engine.add_chat_to_agent(session_id, req.target_key, req.target_key, final)
    game_engine.record_chat(session_id)

    return {
        "success": True,
        "session_id": session_id,
        "agent_key": req.target_key or "dm",
        "reply": final,
        "chat_count": game.get("chat_count", 0),
    }


# ============================
# Agent 行动意图
# ============================

@router.get("/intents/{session_id}/{agent_key}")
async def get_agent_intents(session_id: str, agent_key: str):
    """获取 Agent 当前的行动意图（已生成或空）。"""
    result = game_engine.get_agent_intents(session_id, agent_key)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result)
    return result


@router.post("/intents/{session_id}/{agent_key}/generate")
async def generate_agent_intents(session_id: str, agent_key: str):
    """让 Agent 根据当前局势生成行动意图（插队/私聊/出示证物）。"""
    result = game_engine.generate_agent_intents(session_id, agent_key)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


@router.post("/intents/{session_id}/{agent_key}/approve")
async def approve_agent_intent(session_id: str, agent_key: str, req: ApproveIntentRequest):
    """玩家批准或拒绝 Agent 的某个行动意图。"""
    result = game_engine.approve_intent(session_id, agent_key, req.intent_type, req.approved)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


# ============================
# Agent 发言
# ============================

@router.post("/agent-chat/{session_id}")
async def agent_chat(session_id: str, req: AgentChatRequest):
    """Agent 发言（带角色+记忆+证物感知，自动写入 chat_history）。"""
    game = game_engine.get_game(session_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    # 写入 chat_history
    game_engine.add_chat_to_agent(session_id, req.agent_key, req.role, req.content)
    game_engine.record_chat(session_id, from_agent=req.agent_key, content=req.content)

    return {
        "success": True,
        "session_id": session_id,
        "agent_key": req.agent_key,
        "chat_count": game.get("chat_count", 0),
    }


# ============================
# 发言轮次
# ============================

@router.post("/speak-round/{session_id}/init")
async def init_speak_round(session_id: str):
    """初始化发言轮次——按 companion 顺序排列，DM 不参与。

    进入 investigation 阶段时会自动初始化，也可手动调用重新初始化。
    """
    result = game_engine.init_speak_round(session_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


@router.get("/speak-round/{session_id}")
async def get_speak_round(session_id: str):
    """获取当前发言轮次状态（谁在发言、发言顺序、插队栈、是否轮完）。"""
    result = game_engine.get_speak_round(session_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result)
    return result


@router.post("/speak-round/{session_id}/next")
async def next_speaker(session_id: str):
    """当前发言人结束发言，轮到下一个人。

    前端调用时机：当前发言的 Agent 说完了。
    返回下一个发言人 key，如果 round_complete=True 则本轮结束。
    """
    result = game_engine.next_speaker(session_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


@router.post("/speak-round/{session_id}/interject")
async def interject_speaker(session_id: str, req: InterjectRequest):
    """插队打断——某个 Agent 中途插队发言。

    前端调用时机：Agent 的 interject 意图被玩家批准。
    插队者发言完毕后，调用 /next 回到被打断的位置。
    """
    result = game_engine.interject_speaker(session_id, req.agent_key, req.reason)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


@router.post("/speak-round/{session_id}/new-round")
async def start_new_round(session_id: str):
    """开始新一轮发言（所有人重新按顺序发言）。"""
    result = game_engine.start_new_round(session_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


# ============================
# 私聊系统
# ============================

@router.post("/private-chat/{session_id}/send")
async def send_private_message(session_id: str, req: PrivateMessageRequest):
    """发送私聊消息。

    两人之间的私聊共享一个线程，自动创建。
    消息会写入接收者的 chat_history。
    """
    result = game_engine.send_private_message(
        game_id=session_id,
        from_key=req.from_key,
        to_key=req.to_key,
        content=req.content,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


@router.get("/private-chat/{session_id}/{agent_key}")
async def get_private_threads(session_id: str, agent_key: str):
    """获取某个角色参与的所有私聊线程。"""
    result = game_engine.get_private_threads(session_id, agent_key)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result)
    return result


@router.get("/private-chat/{session_id}/thread/{thread_id}")
async def get_private_thread(session_id: str, thread_id: str):
    """获取指定私聊线程的消息历史。"""
    result = game_engine.get_private_thread(session_id, thread_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result)
    return result


# ============================
# 强制回答
# ============================

@router.post("/force-answer/{session_id}")
async def force_answer(session_id: str, req: ForceAnswerRequest):
    """强制指定 Agent 回答问题。

    被指定的 Agent 插入发言队列最前面，其他角色不可插队。
    回答完毕后调用 /force-answer/{id}/clear 清除状态。
    """
    result = game_engine.force_answer(
        game_id=session_id,
        asker_key=req.asker_key,
        target_key=req.target_key,
        question=req.question,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


@router.post("/force-answer/{session_id}/clear")
async def clear_force_answer(session_id: str):
    """清除强制回答状态（回答完毕后调用）。"""
    result = game_engine.clear_force_answer(session_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    return result


# ============================
# DM 分级提示系统
# ============================

class HintRequest(BaseModel):
    level: int = 1           # 1-4
    discussion_summary: str = ""
    found_clues: list[str] = []
    missed_clues: list[str] = []
    suspects: list[str] = []


@router.post("/hint/{session_id}")
async def dm_generate_hint(session_id: str, req: HintRequest):
    """DM 生成分级提示（L1-L4）。

    L1 - 提醒目标
    L2 - 遗漏信息
    L3 - 推理方向
    L4 - 强提示
    """
    game = game_engine.get_game(session_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    context = {
        "phase": game.get("current_phase", "unknown"),
        "discussion_summary": req.discussion_summary,
        "found_clues": req.found_clues,
        "missed_clues": req.missed_clues,
        "suspects": req.suspects,
    }

    result = orchestrator.dm_generate_hint(level=req.level, context=context)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result)

    if result.get("success"):
        game_engine.record_hint(session_id)

    return result
