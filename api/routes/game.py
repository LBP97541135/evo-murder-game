"""
EvoMap Murder Game - Game Session Routes

游戏 Session 创建、阶段管理、广播、投票、复盘。
v2.1 新增：Agent 游戏状态、意图系统、记忆压缩。
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from api.schemas.invoke_types import GameSessionRequest, GameSessionResponse
from api.agents.agent_orchestrator import AgentRole
from api.agents.game_engine import game_engine, GamePhase
from api.orchestrator import orchestrator
from api.db.models import get_session, Script, ConversationTurn, EvidenceRecord, evidence_record_to_dict

logger = logging.getLogger(__name__)

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
    frontend_phase_index: Optional[int] = None


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


class CastEntry(BaseModel):
    type: str             # "agent" | "player"
    role: str
    agentKey: str = ""
    agent_key: str = ""


class ApplyCastRequest(BaseModel):
    cast: list[CastEntry]
    player_character_name: str = ""


# ============================
# 游戏 Session
# ============================

@router.post("/create-session", response_model=GameSessionResponse)
async def create_game_session(req: GameSessionRequest):
    """创建游戏 Session，同时初始化游戏引擎和所有 Agent 游戏状态。"""
    logger.info(f"Creating game session for script_id={req.script_id}, topic={req.topic}, player_character={req.player_character_name}")
    if not orchestrator.agents:
        logger.error("No agents registered")
        raise HTTPException(status_code=400, detail="No agents registered yet")

    # 校验陪玩 Agent 数量是否足够覆盖剧本角色
    companion_count = len([a for a in orchestrator.agents.values() if a.role == AgentRole.COMPANION])
    db_session = get_session()
    try:
        script = db_session.query(Script).filter(Script.id == req.script_id).first()
        if script:
            playable_count = len([c for c in script.characters if not c.is_victim])
            char_count = playable_count
            logger.info(f"Script '{script.title}' has {char_count} playable characters. Available companions: {companion_count}")
            # 允许 1 名真人玩家，所以需要的陪玩 Agent 数为可玩角色数 - 1（无真人时需全部可玩角色）
            needed_companions = char_count
            if req.player_character_name and req.player_character_name.strip():
                needed_companions = char_count - 1
            if needed_companions > companion_count:
                logger.error(f"Not enough companions. Need {needed_companions}, have {companion_count}")
                raise HTTPException(
                    status_code=400,
                    detail=f"剧本「{script.title}」需要 {needed_companions} 个陪玩 Agent（可玩角色 {char_count} 个"
                           f"{'' if not req.player_character_name else '，含 1 名真人玩家'}），"
                           f"但目前仅有 {companion_count} 个可用",
                )
    finally:
        db_session.close()

    result = orchestrator.create_game_session(
        topic=req.topic,
        script_name=req.script_id,
    )

    if "error" in result:
        logger.error(f"Orchestrator failed to create session: {result}")
        raise HTTPException(status_code=500, detail=result)

    session_id = result.get("session_id", "")
    session_info = orchestrator.sessions.get(session_id, {})

    # 初始化游戏引擎（同时初始化 Agent 游戏状态 + 胶囊注入）
    game_engine.create_game(script_id=req.script_id, session_id=session_id, player_character_name=req.player_character_name)
    from api.capsules.dm_evolution_service import inject_all_capsules_for_agents
    inject_all_capsules_for_agents()
    logger.info(f"Successfully created game session: {session_id}, player_character={req.player_character_name}")

    return GameSessionResponse(
        session_id=session_id,
        participants=session_info.get("companions", []),
        status="active",
    )


@router.post("/cast/{session_id}")
async def apply_game_cast(session_id: str, req: ApplyCastRequest):
    """同步前端选角结果到游戏引擎。"""
    cast_payload = []
    for entry in req.cast:
        item = entry.model_dump()
        if not item.get("agentKey") and item.get("agent_key"):
            item["agentKey"] = item["agent_key"]
        cast_payload.append(item)
    try:
        result = game_engine.apply_cast(
            game_id=session_id,
            cast=cast_payload,
            player_character_name=req.player_character_name or None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"success": True, **result}


@router.get("/role-evidences/{session_id}")
async def get_role_evidences(session_id: str):
    """获取各角色初始分配的证物（2 关联 + 2 随机）。"""
    game = game_engine.get_game(session_id)
    if not game:
        raise HTTPException(status_code=404, detail="game_not_found")
    role_evidences = game.get("role_evidences") or {}
    if not role_evidences:
        for _key, state in game.get("agents", {}).items():
            role_name = (state.character or {}).get("name", "")
            if role_name and state.discovered_evidences:
                role_evidences[role_name] = state.discovered_evidences
    player_role = game.get("player_character_name", "")
    return {
        "success": True,
        "role_evidences": role_evidences,
        "player_role": player_role,
        "player_evidences": role_evidences.get(player_role, []),
    }


@router.get("/public-evidences/{session_id}")
async def get_public_evidences(session_id: str):
    """获取本局已公开出示的证物列表。"""
    game = game_engine.get_game(session_id)
    if not game:
        raise HTTPException(status_code=404, detail="game_not_found")
    return {
        "success": True,
        "public_evidences": game.get("public_evidences") or [],
    }


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
    result = game_engine.force_phase(
        session_id,
        req.phase,
        frontend_phase_index=req.frontend_phase_index,
    )
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


@router.post("/vote/{session_id}/agents")
async def submit_agent_votes(session_id: str):
    """为所有 Agent 角色生成并提交投票。"""
    result = game_engine.submit_agent_votes(session_id)
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


@router.get("/review/{session_id}")
async def get_game_review(session_id: str):
    """获取 DM 复盘包（真相揭示、角色评分、基因与胶囊）。"""
    from api.capsules.dm_evolution_service import get_review_bundle

    bundle = get_review_bundle(session_id)
    if not bundle.get("success") and bundle.get("message") == "review_not_generated":
        return bundle
    return bundle


@router.post("/review/{session_id}/run")
async def run_game_review(session_id: str):
    """运行完整 DM 复盘 + 并行评分 + 基因/胶囊自进化流水线。"""
    from api.capsules.dm_evolution_service import run_full_evolution_pipeline

    try:
        result = run_full_evolution_pipeline(session_id)
        return {"success": True, **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


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
# 角色私人剧本（替代前端硬编码 SCRIPT_CHAPTERS）
# ============================

@router.get("/my-script/{session_id}")
async def get_my_script(session_id: str, character_name: str = "", character_id: str = ""):
    """获取指定角色的私人剧本（章节格式）——用于前端 script-reading 阶段。"""
    logger.info(f"Fetching script for session={session_id}, char_name={character_name}, char_id={character_id}")
    game = game_engine.get_game(session_id)
    if not game:
        logger.error(f"Game not found for session {session_id}")
        raise HTTPException(status_code=404, detail="Game not found")

    # 如果未指定角色名，使用游戏会话中记录的玩家角色名
    if not character_name and not character_id:
        player_char = game.get("player_character_name", "")
        if player_char:
            character_name = player_char
            logger.info(f"Using player_character_name from game: {player_char}")

    # 先从 agent states 中查找角色
    character = {}
    for key, agent_state in game.get("agents", {}).items():
        ch = agent_state.character
        if character_name and ch.get("name") == character_name:
            character = ch
            logger.info(f"Found character {character_name} in agent {key}")
            break
        if character_id and ch.get("id") == character_id:
            character = ch
            logger.info(f"Found character ID {character_id} in agent {key}")
            break

    # 侦探/观战身份：返回全局故事，不查嫌疑人角色表
    observer_names = {"侦探", "林晓青", "林晓青 · 侦探", "林晓青·侦探"}
    is_observer = (
        character_name in observer_names
        or (character_name and character_name.startswith("林晓青"))
    )

    # 从数据库加载剧本和 global_story（统一一次查询）
    db_session = get_session()
    global_story = ""
    try:
        script = db_session.query(Script).filter(Script.id == game.get("script_id", "")).first()
        if script:
            global_story = script.global_story or ""

        if is_observer:
            chapters = []
            if global_story:
                chapters.append({"title": "序幕 · 故事背景", "content": global_story})
            if not chapters:
                chapters.append({
                    "title": "侦探手册",
                    "content": "你以第三方侦探身份参与本案调查，可质询、搜证与投票，但不掌握嫌疑人秘密。",
                })
            return {
                "success": True,
                "character_name": "林晓青 · 侦探",
                "character_id": "",
                "image": "",
                "role_type": "detective",
                "is_killer": False,
                "is_victim": False,
                "is_observer": True,
                "chapters": chapters,
            }

        # 未在 agent states 中找到 → 从数据库角色表查找
        if script and not character:
            logger.info(f"Character {character_name}/{character_id} not found in agents, checking database...")
            for ch_obj in script.characters:
                if character_name and ch_obj.name == character_name:
                    character = {
                        "id": ch_obj.id, "name": ch_obj.name,
                        "bio": ch_obj.bio or "", "personality": ch_obj.personality or "",
                        "context": ch_obj.context or "", "secret": ch_obj.secret or "",
                        "violation": ch_obj.violation or "",
                        "image": ch_obj.image_filename or ch_obj.image or "",
                        "roleType": ch_obj.role_type,
                        "isKiller": ch_obj.is_killer, "isVictim": ch_obj.is_victim,
                    }
                    break
                if character_id and ch_obj.id == character_id:
                    character = {
                        "id": ch_obj.id, "name": ch_obj.name,
                        "bio": ch_obj.bio or "", "personality": ch_obj.personality or "",
                        "context": ch_obj.context or "", "secret": ch_obj.secret or "",
                        "violation": ch_obj.violation or "",
                        "image": ch_obj.image_filename or ch_obj.image or "",
                        "roleType": ch_obj.role_type,
                        "isKiller": ch_obj.is_killer, "isVictim": ch_obj.is_victim,
                    }
                    break
            # 降级：返回第一个 is_player 角色，或第一个角色
            if not character and not character_name and not character_id:
                for ch_obj in script.characters:
                    if ch_obj.is_player:
                        character = {
                            "id": ch_obj.id, "name": ch_obj.name,
                            "bio": ch_obj.bio or "", "personality": ch_obj.personality or "",
                            "context": ch_obj.context or "", "secret": ch_obj.secret or "",
                            "violation": ch_obj.violation or "",
                            "image": ch_obj.image_filename or ch_obj.image or "",
                            "roleType": ch_obj.role_type,
                            "isKiller": ch_obj.is_killer, "isVictim": ch_obj.is_victim,
                        }
                        break
                if not character and script.characters:
                    ch_obj = script.characters[0]
                    character = {
                        "id": ch_obj.id, "name": ch_obj.name,
                        "bio": ch_obj.bio or "", "personality": ch_obj.personality or "",
                        "context": ch_obj.context or "", "secret": ch_obj.secret or "",
                        "violation": ch_obj.violation or "",
                        "image": ch_obj.image_filename or ch_obj.image or "",
                        "roleType": ch_obj.role_type,
                        "isKiller": ch_obj.is_killer, "isVictim": ch_obj.is_victim,
                    }
    finally:
        db_session.close()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    # 构建章节
    chapters = []
    ch_name = character.get("name", "未知角色")

    if global_story:
        chapters.append({"title": "序幕 · 故事背景", "content": global_story})

    bio = character.get("bio", "")
    context = character.get("context", "")
    if bio or context:
        chapters.append({
            "title": f"第一章 · {ch_name}的背景",
            "content": f"{bio}\n\n{context}" if bio and context else (bio or context),
        })

    secret = character.get("secret", "")
    if secret:
        chapters.append({"title": f"第二章 · {ch_name}的秘密", "content": secret})

    violation = character.get("violation", "")
    if violation:
        chapters.append({"title": f"第三章 · {ch_name}的行为限制", "content": violation})

    if not chapters:
        chapters.append({"title": "剧本", "content": "（暂无角色剧本数据）"})

    return {
        "success": True,
        "character_name": ch_name,
        "character_id": character.get("id", ""),
        "image": character.get("image", ""),
        "role_type": character.get("roleType", ""),
        "is_killer": character.get("isKiller", False),
        "is_victim": character.get("isVictim", False),
        "chapters": chapters,
    }


# ============================
# 游戏状态快照（替代已回退的 /game/snapshot）
# ============================

@router.get("/snapshot/{session_id}")
async def get_game_snapshot(session_id: str):
    """一站式恢复游戏状态——前端页面刷新后用于重建全部 UI 状态。

    返回：阶段、角色映射、证物列表、对话记录、投票结果、后剧情数据。
    """
    game = game_engine.get_game(session_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    phase_info = game_engine.get_phase_info(session_id)
    if "error" in phase_info:
        raise HTTPException(status_code=404, detail=phase_info["error"])

    # Agent 状态摘要
    agents_info = []
    for key, agent_state in game.get("agents", {}).items():
        ch = agent_state.character
        agents_info.append({
            "key": key,
            "name": ch.get("name", key),
            "character_id": ch.get("id", ""),
            "role_type": ch.get("roleType", "unknown"),
            "is_killer": ch.get("isKiller", False),
            "is_victim": ch.get("isVictim", False),
            "image": ch.get("image", ""),
            "bio": ch.get("bio", ""),
            "personality": ch.get("personality", ""),
            "has_intents": any(v is not None for v in (agent_state.intents or {}).values()),
        })

    # 对话记录（用于事件重建）
    conversation_events = []
    db_session = get_session()
    try:
        conversations = db_session.query(ConversationTurn).filter(
            ConversationTurn.session_id == session_id
        ).order_by(ConversationTurn.created_at.asc()).all()
        for conv in conversations:
            conversation_events.append({
                "actor_name": conv.actor_name,
                "final_response": conv.final_response or conv.original_response,
                "created_at": conv.created_at.isoformat() if conv.created_at else "",
            })
    finally:
        db_session.close()

    # 证物列表
    evidence_list = []
    ev_session = get_session()
    try:
        evidences = ev_session.query(EvidenceRecord).filter(
            EvidenceRecord.session_id == session_id,
        ).all()
        evidence_list = [evidence_record_to_dict(e) for e in evidences]
    finally:
        ev_session.close()

    # 前端阶段映射（搜证与讨论共用 investigation，需持久化 frontend_phase_index）
    backend_phase = game.get("current_phase", "intro")
    frontend_phase_map = {
        "intro": 2,
        "investigation": 3,
        "voting": 5,
        "reveal": 6,
        "review": 7,
    }
    stored_frontend_index = game.get("frontend_phase_index")
    if stored_frontend_index is not None:
        frontend_phase_index = stored_frontend_index
    else:
        frontend_phase_index = frontend_phase_map.get(backend_phase, 0)
        if backend_phase == "investigation" and game.get("chat_count", 0) >= 1:
            frontend_phase_index = max(frontend_phase_index, 4)

    return {
        "success": True,
        "session_id": session_id,
        "script_id": game.get("script_id", ""),
        "backend_phase": backend_phase,
        "frontend_phase_index": frontend_phase_index,
        "agents": agents_info,
        "evidences": evidence_list,
        "conversations": conversation_events,
        "vote_result": game.get("vote_result"),
        "reveal_data": game.get("reveal_data"),
        "phase_history": game.get("phase_history", []),
        "chat_count": game.get("chat_count", 0),
        "hints_used": game.get("hints_used", 0),
        "started_at": game.get("started_at", ""),
        "cast": game.get("cast", []),
        "player_character_name": game.get("player_character_name", ""),
        "role_evidences": game.get("role_evidences", {}),
        "public_evidences": game.get("public_evidences", []),
        "dm_review": game.get("dm_review"),
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

    from api.agents.game_context import find_agent_key
    target_key = find_agent_key(game, req.agent_key) or req.agent_key

    # 写入 chat_history
    game_engine.add_chat_to_agent(session_id, target_key, req.role, req.content)
    game_engine.record_chat(session_id, from_agent=target_key, content=req.content)

    return {
        "success": True,
        "session_id": session_id,
        "agent_key": target_key,
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
    """公共喊话——被喊话者须立刻回复，但不改变发言队列顺序。"""
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
