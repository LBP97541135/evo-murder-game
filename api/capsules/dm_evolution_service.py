"""
DM 复盘评分与自进化流水线

流程：
  1. DM 揭示真相 + 指出讨论不足
  2. DM 并行给每个角色 8 维度打分 + 评语
  3. 各 Agent 自评生成 Gene → DM 评审 → 生成胶囊（每 Agent 至少 1 个）
  4. 胶囊入库（CapsuleRecord.review_status=approved）
"""

from __future__ import annotations

import json
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any, Optional

from api.llm.llm_service import respond_initial

logger = logging.getLogger(__name__)

CAPSULE_SCORE_THRESHOLD = 0.6

EXCLUDED_SCORE_ROLE_NAMES = frozenset({
    "侦探", "DM", "雾港主理人", "dm", "host", "narrator",
})

SCORE_DIMENSIONS = [
    {"key": "evidenceCount", "label": "搜证数量", "description": "主动搜索与发现的线索数量"},
    {"key": "clueMastery", "label": "线索掌握度", "description": "对线索的理解深度与关联能力"},
    {"key": "logicClarity", "label": "条理清晰度", "description": "发言结构与推理链完整度"},
    {"key": "activity", "label": "活跃度", "description": "发言频率与参与讨论的积极性"},
    {"key": "progress", "label": "推进度", "description": "对游戏进程的关键推动程度"},
    {"key": "roleImmersion", "label": "角色代入度", "description": "是否始终以角色身份行动和发言"},
    {"key": "collaboration", "label": "协作度", "description": "与其他玩家配合程度"},
    {"key": "reasoningAccuracy", "label": "推理准确度", "description": "最终结论与真相的接近程度"},
]

DM_CHARACTER_SCORE_PROMPT = """你是剧本杀 DM「{dm_name}」，正在对本局游戏进行专业复盘评分。

## 案件与真相
{truth_context}

## 本局讨论摘要
{discussion_summary}

## 待评角色
- 角色名：{character_name}
- 扮演者：{agent_name}（{role_type}）
- 是否被指认为凶手：{is_accused}
- 该角色发言摘录：
{speech_excerpt}

## 评分维度（每项 0-100 整数）
{dimensions_text}

## 输出要求
请严格输出 JSON，不要其他内容：
{{
  "compositeScore": 75,
  "dimensions": {{
    "evidenceCount": 70,
    "clueMastery": 72,
    "logicClarity": 80,
    "activity": 65,
    "progress": 70,
    "roleImmersion": 85,
    "collaboration": 78,
    "reasoningAccuracy": 68
  }},
  "dmComment": "2-4 句话的综合评语，指出亮点与不足，语气专业公正"
}}"""


def _resolve_agent_db_id(node_id: str) -> Optional[str]:
    from api.db.models import get_session, AgentNode

    if not node_id:
        return None
    db = get_session()
    try:
        row = db.query(AgentNode).filter(AgentNode.node_id == node_id).first()
        if row:
            return row.id
        row = db.query(AgentNode).filter(AgentNode.id == node_id).first()
        return row.id if row else None
    finally:
        db.close()


def _is_excluded_score_role(role_name: str) -> bool:
    name = (role_name or "").strip()
    if not name:
        return True
    if name in EXCLUDED_SCORE_ROLE_NAMES:
        return True
    lowered = name.lower()
    return lowered in {"dm", "host", "narrator", "detective"}


def _is_review_participant(p: dict) -> bool:
    from api.orchestrator import orchestrator

    role_name = p.get("role_name", "")
    if _is_excluded_score_role(role_name):
        return False
    agent_key = p.get("agent_key", "")
    if agent_key and agent_key not in ("user", ""):
        agent = orchestrator.agents.get(agent_key)
        if agent and agent.role.value == "dm":
            return False
    return bool(role_name)


def _filter_character_scores(scores: list[dict]) -> list[dict]:
    from api.orchestrator import orchestrator

    filtered: list[dict] = []
    for score in scores:
        role_name = score.get("role_name", "")
        if _is_excluded_score_role(role_name):
            continue
        agent_key = score.get("agent_key", "")
        if agent_key and agent_key not in ("user", ""):
            agent = orchestrator.agents.get(agent_key)
            if agent and agent.role.value == "dm":
                continue
        filtered.append(score)
    return filtered


def _load_agent_states_for_session(session_id: str) -> dict[str, dict]:
    """从 agent_game_states 表加载本局 Agent 状态摘要。"""
    from api.agents.game_engine import AgentGameState
    from api.db.models import get_session, AgentGameStateModel

    agents: dict[str, dict] = {}
    db = get_session()
    try:
        rows = db.query(AgentGameStateModel).filter(
            AgentGameStateModel.session_id == session_id
        ).all()
        for ast in rows:
            state = AgentGameState.from_db_dict({
                "agent_key": ast.agent_key,
                "session_id": ast.session_id,
                "character_json": ast.character_json or {},
                "constitution": ast.constitution or "",
                "all_actors_json": ast.all_actors_json or [],
                "global_story": ast.global_story or "",
                "chat_history_json": ast.chat_history_json or [],
                "compressed_summary": ast.compressed_summary or "",
                "key_facts_json": ast.key_facts_json or [],
                "discovered_evidences_json": ast.discovered_evidences_json or [],
                "intents_json": ast.intents_json or {},
                "observation_buffer_json": ast.observation_buffer_json or [],
                "loaded_capsule_ids_json": ast.loaded_capsule_ids_json or [],
            })
            agents[ast.agent_key] = state
    except Exception as exc:
        logger.warning(f"加载 agent_game_states 失败: {exc}")
    finally:
        db.close()
    return agents


def _infer_participants_from_conversations(session_id: str, player_role: str) -> list[dict]:
    """cast 缺失时，从对话记录推断本局参与角色。"""
    from api.db.models import get_session, ConversationTurn

    db = get_session()
    try:
        rows = db.query(ConversationTurn).filter(
            ConversationTurn.session_id == session_id
        ).all()
    finally:
        db.close()

    role_names: set[str] = set()
    for conv in rows:
        actor = (conv.actor_name or "").strip()
        if not actor or actor in ("未知", "player", "user"):
            continue
        if _is_excluded_score_role(actor):
            continue
        if "Agent" in actor or " · " in actor:
            role_names.add(actor.split(" · ")[0].strip())
        else:
            role_names.add(actor)

    participants: list[dict] = []
    for role_name in sorted(role_names):
        if _is_excluded_score_role(role_name):
            continue
        p_type = "human" if player_role and role_name == player_role else "agent"
        participants.append({
            "role_name": role_name,
            "agent_key": "user" if p_type == "human" else "",
            "type": p_type,
        })
    return participants


def _resolve_agent_key_for_role(game: dict, role_name: str, agent_states: dict | None = None) -> str:
    from api.orchestrator import orchestrator

    for entry in game.get("cast") or []:
        if entry.get("role") == role_name and entry.get("type") == "agent":
            raw = entry.get("agentKey") or entry.get("agent_key") or ""
            if raw in orchestrator.agents:
                return raw
            for ok, agent in orchestrator.agents.items():
                if agent.name == raw or ok == raw or ok.endswith(f"_{raw}"):
                    return ok

    for key, state in (agent_states or game.get("agents") or {}).items():
        ch = state.character if hasattr(state, "character") else (state.get("character") if isinstance(state, dict) else {})
        if (ch or {}).get("name") == role_name:
            return key

    for ok, agent in orchestrator.agents.items():
        if agent.role.value == "companion" and agent.name == role_name:
            return ok
    return ""


def _agent_state_chat_len(state: Any) -> int:
    history = getattr(state, "chat_history", None)
    if history is None and isinstance(state, dict):
        history = state.get("chat_history")
    return len(history or [])


def _resolve_best_agent_for_role(
    game: dict,
    role_name: str,
    agent_states: dict | None = None,
) -> str:
    """为剧本角色解析唯一陪玩 Agent；多名候选时取本局对话最活跃者。"""
    from api.orchestrator import orchestrator

    cast_key = _resolve_agent_key_for_role(game, role_name, agent_states)
    if cast_key:
        agent = orchestrator.agents.get(cast_key)
        if agent and agent.role.value != "dm":
            return cast_key

    states = agent_states or game.get("agents") or {}
    candidates: list[tuple[str, int]] = []
    for key, state in states.items():
        ch = state.character if hasattr(state, "character") else (
            state.get("character") if isinstance(state, dict) else {}
        )
        if (ch or {}).get("name") != role_name:
            continue
        agent = orchestrator.agents.get(key)
        if not agent or agent.role.value == "dm":
            continue
        candidates.append((key, _agent_state_chat_len(state)))

    if candidates:
        return max(candidates, key=lambda item: item[1])[0]
    return ""


def _participating_agent_roles(game: dict, session_id: str) -> list[str]:
    """本局由 Agent 扮演的剧本角色名（不含玩家/DM）。"""
    cast = game.get("cast") or []
    if cast:
        return [
            entry.get("role", "")
            for entry in cast
            if entry.get("type") == "agent" and entry.get("role")
        ]

    player_role = game.get("player_character_name", "")
    inferred = _infer_participants_from_conversations(session_id, player_role)
    return [
        p["role_name"]
        for p in inferred
        if p.get("type") == "agent" and p.get("role_name")
    ]


def _enrich_participants_with_agent_keys(
    participants: list[dict],
    game: dict,
    agent_states: dict,
) -> list[dict]:
    """为参与列表中的 Agent 角色补全 agent_key（每角色仅一名 Agent）。"""
    enriched: list[dict] = []
    for p in participants:
        entry = dict(p)
        if entry.get("type") == "agent":
            role_name = entry.get("role_name", "")
            if role_name and not entry.get("agent_key"):
                entry["agent_key"] = _resolve_best_agent_for_role(game, role_name, agent_states)
        enriched.append(entry)
    return enriched


def _gather_session_context(session_id: str) -> dict:
    from api.agents.game_engine import game_engine
    from api.db.models import get_session, ConversationTurn, Script

    game = game_engine.get_game(session_id) or {}
    script_id = game.get("script_id", "")
    truth_killer = ""
    script_title = ""

    db = get_session()
    try:
        script = db.query(Script).filter(Script.id == script_id).first() if script_id else None
        if script:
            script_title = script.title or script_id
            truth_killer = getattr(script, "killer_role", "") or script.fixed_killer or ""

        conversations = (
            db.query(ConversationTurn)
            .filter(ConversationTurn.session_id == session_id)
            .order_by(ConversationTurn.created_at.asc())
            .all()
        )
        speech_lines = []
        speech_by_role: dict[str, list[str]] = {}
        for conv in conversations:
            text = (conv.final_response or conv.original_response or "").strip()
            if not text:
                continue
            role = conv.actor_name or "未知"
            line = f"{role}：{text[:300]}"
            speech_lines.append(line)
            speech_by_role.setdefault(role, []).append(text[:400])
    finally:
        db.close()

    vote = game.get("vote_result") or {}
    reveal = game.get("reveal_data") or {}
    cast = game.get("cast") or []

    participants = []
    for entry in cast:
        if entry.get("type") == "agent":
            role_name = entry.get("role", "")
            agent_key = entry.get("agentKey") or entry.get("agent_key", "")
            participants.append({
                "role_name": role_name,
                "agent_key": agent_key,
                "type": "agent",
            })
        elif entry.get("type") in ("human", "player"):
            participants.append({
                "role_name": entry.get("role", ""),
                "agent_key": "user",
                "type": "human",
            })

    player_role = game.get("player_character_name", "")
    if player_role and not any(p["role_name"] == player_role for p in participants):
        participants.append({"role_name": player_role, "agent_key": "user", "type": "human"})

    agent_states = _load_agent_states_for_session(session_id)

    if not any(p.get("type") == "agent" for p in participants):
        inferred = _infer_participants_from_conversations(session_id, player_role)
        for p in inferred:
            role = p.get("role_name", "")
            if role and not any(x["role_name"] == role for x in participants):
                participants.append(p)

    participants = _enrich_participants_with_agent_keys(participants, game, agent_states)

    if not participants:
        participants = _infer_participants_from_conversations(session_id, player_role)
        participants = _enrich_participants_with_agent_keys(participants, game, agent_states)

    participants = [p for p in participants if _is_review_participant(p)]
    seen_roles: set[str] = set()
    seen_agent_keys: set[str] = set()
    deduped: list[dict] = []
    for p in participants:
        role = p.get("role_name", "")
        agent_key = p.get("agent_key", "")
        if p.get("type") == "agent" and agent_key:
            if agent_key in seen_agent_keys:
                continue
            seen_agent_keys.add(agent_key)
        if role in seen_roles:
            continue
        seen_roles.add(role)
        deduped.append(p)
    participants = deduped

    return {
        "session_id": session_id,
        "script_id": script_id,
        "script_title": script_title,
        "truth_killer": truth_killer,
        "vote_result": vote,
        "reveal_data": reveal,
        "discussion_summary": "\n".join(speech_lines[-40:]) or "（本局公共讨论记录较少）",
        "speech_by_role": speech_by_role,
        "participants": participants,
        "agent_states": agent_states,
        "chat_count": game.get("chat_count", 0),
    }


def dm_generate_truth_review(session_id: str, context: dict | None = None) -> dict:
    """DM 揭示真相：还原案件 + 指出讨论过程不足。"""
    ctx = context or _gather_session_context(session_id)
    reveal = ctx.get("reveal_data") or {}
    vote = ctx.get("vote_result") or {}

    prompt = f"""你是剧本杀 DM，正在对本局《{ctx.get('script_title', '未知剧本')}》做完整复盘。

## 投票结果
- 玩家指认凶手：{vote.get('killer', '未知')}
- 是否正确：{'是' if vote.get('is_correct') else '否'}
- 真实凶手：{ctx.get('truth_killer') or '（见剧本设定）'}

## 已有真相材料
凶手交代：{reveal.get('killer_confession', '（暂无）')[:500]}
DM 揭晓：{reveal.get('truth', '（暂无）')[:500]}

## 讨论过程摘要
{ctx.get('discussion_summary', '')[:3000]}

请输出 JSON：
{{
  "truth_narrative": "200-350字完整真相还原（含动机、手法、时间线）",
  "discussion_critique": "150-250字指出本局讨论中的主要不足（遗漏线索、逻辑跳跃、角色行为问题等）",
  "key_lessons": ["本局可改进点1", "本局可改进点2", "本局可改进点3"],
  "vote_analysis": "50-100字对投票结果的评价"
}}"""

    try:
        raw = respond_initial(
            system_prompt="你是专业剧本杀 DM，擅长复盘总结与教学。严格输出 JSON。",
            user_message=prompt,
            temperature=0.5,
            max_tokens=1500,
        )
        parsed = _parse_json(raw)
        return {"success": True, **parsed}
    except Exception as e:
        logger.error(f"DM truth review failed: {e}")
        return {
            "success": True,
            "truth_narrative": reveal.get("truth") or f"真凶为{ctx.get('truth_killer', '待揭晓')}。",
            "discussion_critique": "本局讨论记录不足，建议下次更充分交流线索与时间线。",
            "key_lessons": ["多关注时间线矛盾", "关键证物要及时公开讨论"],
            "vote_analysis": "投票结果已记录，可参考 DM 评分进一步复盘。",
        }


def _score_one_character(participant: dict, ctx: dict, dm_name: str) -> dict:
    role_name = participant["role_name"]
    speeches = ctx.get("speech_by_role", {}).get(role_name, [])
    excerpt = "\n".join(f"- {s[:200]}" for s in speeches[-6:]) or "（该角色本局几乎未发言）"

    accused = ctx.get("vote_result", {}).get("killer", "")
    dims_text = "\n".join(f"- {d['key']} {d['label']}：{d['description']}" for d in SCORE_DIMENSIONS)

    from api.orchestrator import orchestrator

    agent_key = participant.get("agent_key", "")
    agent = orchestrator.agents.get(agent_key) if agent_key not in ("user", "") else None
    agent_name = agent.name if agent else ("玩家" if participant.get("type") == "human" else role_name)

    truth_ctx = (
        f"剧本《{ctx.get('script_title')}》\n"
        f"真凶：{ctx.get('truth_killer')}\n"
        f"投票指认：{accused}\n"
        f"投票正确：{ctx.get('vote_result', {}).get('is_correct')}"
    )

    prompt = DM_CHARACTER_SCORE_PROMPT.format(
        dm_name=dm_name,
        truth_context=truth_ctx,
        discussion_summary=ctx.get("discussion_summary", "")[:2000],
        character_name=role_name,
        agent_name=agent_name,
        role_type="AI Agent" if participant.get("type") == "agent" else "真人玩家",
        is_accused="是" if role_name == accused else "否",
        speech_excerpt=excerpt,
        dimensions_text=dims_text,
    )

    try:
        raw = respond_initial(
            system_prompt="你是剧本杀 DM 评分专家。按 JSON 格式输出，dimensions 每项为 0-100 整数。",
            user_message=prompt,
            temperature=0.35,
            max_tokens=800,
        )
        parsed = _parse_json(raw)
        dims = parsed.get("dimensions") or {}
        for d in SCORE_DIMENSIONS:
            dims.setdefault(d["key"], 60)
        composite = int(parsed.get("compositeScore") or sum(dims.values()) // max(len(dims), 1))
        return {
            "role_name": role_name,
            "agent_key": agent_key,
            "participant_type": participant.get("type", "agent"),
            "agent_name": agent_name,
            "compositeScore": max(0, min(100, composite)),
            "dimensions": {k: max(0, min(100, int(dims.get(k, 60)))) for k in [d["key"] for d in SCORE_DIMENSIONS]},
            "dmComment": parsed.get("dmComment") or f"{role_name} 本局表现中等，仍有提升空间。",
        }
    except Exception as e:
        logger.warning(f"Score failed for {role_name}: {e}")
        default_dims = {d["key"]: 65 for d in SCORE_DIMENSIONS}
        return {
            "role_name": role_name,
            "agent_key": agent_key,
            "participant_type": participant.get("type", "agent"),
            "agent_name": agent_name,
            "compositeScore": 65,
            "dimensions": default_dims,
            "dmComment": f"{role_name} 本局表现已记录，详细评语生成失败，请稍后重试。",
        }


def dm_score_characters_parallel(session_id: str, context: dict | None = None) -> list[dict]:
    """DM 并行给每个角色打分。"""
    ctx = context or _gather_session_context(session_id)
    from api.orchestrator import orchestrator

    dm_agents = [a for a in orchestrator.agents.values() if a.role.value == "dm"]
    dm_name = dm_agents[0].name if dm_agents else "雾港主理人"

    participants = ctx.get("participants") or []
    if not participants:
        return []

    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=min(6, len(participants))) as pool:
        futures = {
            pool.submit(_score_one_character, p, ctx, dm_name): p
            for p in participants
        }
        for fut in as_completed(futures):
            try:
                results.append(fut.result())
            except Exception as e:
                p = futures[fut]
                logger.error(f"Parallel score error: {e}")

    results.sort(key=lambda x: x.get("role_name", ""))
    return _filter_character_scores(results)


def _agent_self_reflect_gene(
    session_id: str,
    agent_key: str,
    character_score: dict | None,
    ctx: dict,
) -> dict:
    """Agent 自评并创建 Gene。"""
    from api.orchestrator import orchestrator
    from api.capsules.capsule_service import create_gene

    agent = orchestrator.agents.get(agent_key)
    if not agent or not agent.node_id:
        return {"error": "agent_not_found", "agent_key": agent_key}

    db_id = _resolve_agent_db_id(agent.node_id)
    if not db_id:
        return {"error": "agent_db_not_found", "agent_key": agent_key}

    score_data = character_score or {}
    composite = score_data.get("compositeScore", 70)
    self_score = max(0.0, min(1.0, composite / 100.0))

    prompt = f"""你是 Agent「{agent.name}」，角色类型 {agent.role.value}。
刚完成剧本《{ctx.get('script_title')}》的一局游戏。

## DM 对你的评分
综合分：{composite}
评语：{score_data.get('dmComment', '')}
维度：{json.dumps(score_data.get('dimensions', {}), ensure_ascii=False)}

## 讨论摘要
{ctx.get('discussion_summary', '')[:1500]}

请以第一人称写局后自我分析（150-250字），并提炼一条可复用的经验策略。
输出 JSON：
{{"summary": "50字经验摘要", "detail": "完整自我分析", "category": "role-playing或hosting或reasoning", "signals": ["标签1","标签2"], "self_score": 0.75}}"""

    try:
        raw = respond_initial(
            system_prompt="你是能自我反思的剧本杀 Agent。严格输出 JSON。",
            user_message=prompt,
            temperature=0.6,
            max_tokens=900,
        )
        parsed = _parse_json(raw)
        self_score = float(parsed.get("self_score", self_score))
        summary = parsed.get("summary") or f"{agent.name} 本局复盘"
        detail = parsed.get("detail") or summary
        category = parsed.get("category") or ("hosting" if agent.role.value == "dm" else "role-playing")
        signals = parsed.get("signals") or agent.domains[:3]
    except Exception:
        summary = f"{agent.name} 本局复盘 - 会话 {session_id[:8]}"
        detail = score_data.get("dmComment", summary)
        category = "hosting" if agent.role.value == "dm" else "role-playing"
        signals = list(agent.domains[:3])

    return create_gene(
        agent_node_id=db_id,
        session_id=session_id,
        script_id=ctx.get("script_id", ""),
        signals=signals,
        category=category,
        status="completed",
        score=self_score,
        summary=summary,
        detail=detail,
    )


def _session_companion_agent_keys(game: dict, session_id: str, ctx: dict | None = None) -> list[str]:
    """本局参与复盘自进化的 Agent：仅实际参与本局的陪玩 companion，不含 DM。"""
    from api.orchestrator import orchestrator

    keys: list[str] = []
    ctx = ctx or {}
    agent_states = ctx.get("agent_states") or _load_agent_states_for_session(session_id)

    def _append(key: str | None) -> None:
        if not key or key in keys:
            return
        agent = orchestrator.agents.get(key)
        if not agent or agent.role.value == "dm":
            return
        if not agent.node_id or not _resolve_agent_db_id(agent.node_id):
            return
        keys.append(key)

    for entry in game.get("cast") or []:
        if entry.get("type") != "agent":
            continue
        raw = entry.get("agentKey") or entry.get("agent_key")
        if raw in orchestrator.agents:
            _append(raw)
        else:
            for ok, agent in orchestrator.agents.items():
                if agent.name == raw or ok == raw or ok.endswith(f"_{raw}"):
                    _append(ok)
                    break

    if not keys:
        for role_name in _participating_agent_roles(game, session_id):
            _append(_resolve_best_agent_for_role(game, role_name, agent_states))

    if not keys:
        for participant in ctx.get("participants") or []:
            if participant.get("type") != "agent":
                continue
            role_name = participant.get("role_name", "")
            resolved = participant.get("agent_key") or _resolve_best_agent_for_role(
                game, role_name, agent_states
            )
            _append(resolved)

    if not keys:
        for key in _infer_companion_keys_from_conversations(session_id, game, agent_states):
            _append(key)

    # cast 缺失时：补充本局有私聊/发言记录但未出现在公共对话角色名中的 Agent
    if not game.get("cast"):
        for key, state in agent_states.items():
            if _agent_state_chat_len(state) > 0:
                _append(key)

    return keys


def _infer_companion_keys_from_conversations(
    session_id: str,
    game: dict | None = None,
    agent_states: dict | None = None,
) -> list[str]:
    """从对话里的 Agent 名称或剧本角色名推断本局实际出场的陪玩 Agent。"""
    from api.db.models import get_session, ConversationTurn
    from api.orchestrator import orchestrator

    db = get_session()
    try:
        rows = db.query(ConversationTurn).filter(
            ConversationTurn.session_id == session_id
        ).all()
    finally:
        db.close()

    keys: list[str] = []
    companion_by_name = {
        agent.name: ok
        for ok, agent in orchestrator.agents.items()
        if agent.role.value == "companion"
    }
    game = game or {}
    agent_states = agent_states or {}
    player_role = game.get("player_character_name", "")

    seen_roles: set[str] = set()
    for conv in rows:
        actor = (conv.actor_name or "").strip()
        if not actor or _is_excluded_score_role(actor):
            continue
        if actor in companion_by_name:
            if companion_by_name[actor] not in keys:
                keys.append(companion_by_name[actor])
            continue
        if " · " in actor:
            agent_label = actor.split(" · ", 1)[1].replace(" Agent", "").strip()
            for name, ok in companion_by_name.items():
                if name == agent_label and ok not in keys:
                    keys.append(ok)
                    break
            continue
        role_name = actor.split(" · ")[0].strip() if " · " in actor else actor
        if role_name in seen_roles or (player_role and role_name == player_role):
            continue
        seen_roles.add(role_name)
        resolved = _resolve_best_agent_for_role(game, role_name, agent_states)
        if resolved and resolved not in keys:
            keys.append(resolved)
    return keys


def _build_capsule_display_for_gene(
    gene_id: str,
    agent_key: str,
    agent_name: str,
    min_composite: float = CAPSULE_SCORE_THRESHOLD,
) -> dict:
    """DM 评审 Gene 并生成胶囊；无论是否入库都返回可展示结构。"""
    from api.db.models import get_session, GeneRecord
    from api.capsules.capsule_service import (
        dm_review_gene,
        generate_capsule_from_gene,
        get_capsule,
        get_gene,
        _extract_capsule_content,
    )

    review = dm_review_gene(gene_id)
    if "error" in review:
        return review

    db = get_session()
    try:
        gene_row = db.query(GeneRecord).filter(GeneRecord.id == gene_id).first()
        if not gene_row:
            return {"error": "gene_not_found"}
        composite = gene_row.score * 0.3 + (gene_row.dm_score or 0) * 0.7
        if composite < min_composite:
            gene_row.dm_score = max(gene_row.dm_score or 0, min_composite)
            db.commit()
    finally:
        db.close()

    cap = generate_capsule_from_gene(gene_id)
    if cap.get("error") == "score_too_low":
        db = get_session()
        try:
            gene_row = db.query(GeneRecord).filter(GeneRecord.id == gene_id).first()
            if gene_row:
                gene_row.dm_score = 0.85
                db.commit()
        finally:
            db.close()
        cap = generate_capsule_from_gene(gene_id)

    if cap.get("success") and cap.get("capsule_id"):
        stored = get_capsule(cap["capsule_id"]) or {}
        return {
            **stored,
            "agent_key": agent_key,
            "agent_name": agent_name,
            "geneId": gene_id,
            "stored_in_db": True,
            "dm_review": review,
        }

    gene = get_gene(gene_id)
    if not gene:
        return {"error": "gene_not_found"}

    db = get_session()
    try:
        gene_row = db.query(GeneRecord).filter(GeneRecord.id == gene_id).first()
        if not gene_row:
            return {"error": "gene_not_found"}
        content = _extract_capsule_content(gene_row, "companion")
        composite = gene_row.score * 0.3 + (gene_row.dm_score or 0) * 0.7
    finally:
        db.close()

    return {
        "id": f"preview_{gene_id}",
        "geneId": gene_id,
        "agent_key": agent_key,
        "agent_name": agent_name,
        "title": content.get("title") or f"{agent_name} 本局经验胶囊",
        "category": gene.get("category"),
        "content": content.get("content") or gene.get("summary") or "",
        "strategy": content.get("strategy") or gene.get("dmSuggestions") or "",
        "examples": content.get("examples") or "",
        "antiPatterns": content.get("anti_patterns") or "",
        "score": composite,
        "stored_in_db": False,
        "reviewStatus": "preview",
        "dm_review": review,
    }


def run_full_evolution_pipeline(session_id: str) -> dict:
    """完整复盘自进化流水线（评分含玩家+陪玩 Agent；基因/胶囊仅陪玩 Agent）。"""
    from api.agents.game_engine import game_engine
    from api.orchestrator import orchestrator
    from api.capsules.capsule_service import get_gene

    ctx = _gather_session_context(session_id)
    game = game_engine.get_game(session_id) or {}

    truth_review = dm_generate_truth_review(session_id, ctx)
    character_scores = dm_score_characters_parallel(session_id, ctx)

    genes: list[dict] = []
    capsules: list[dict] = []
    errors: list[str] = []

    agent_keys = _session_companion_agent_keys(game, session_id, ctx)
    if not agent_keys:
        errors.append("no_companion_agents_resolved")

    agent_states = ctx.get("agent_states") or {}

    for agent_key in agent_keys:
        agent = orchestrator.agents.get(agent_key)
        if not agent:
            errors.append(f"{agent_key}: agent_not_found")
            continue

        char_score = None
        role_name = None
        for entry in game.get("cast") or []:
            if (entry.get("agentKey") or entry.get("agent_key")) == agent_key:
                role_name = entry.get("role")
                break
        if not role_name:
            state = agent_states.get(agent_key) or game.get("agents", {}).get(agent_key)
            if state:
                ch = state.character if hasattr(state, "character") else {}
                role_name = (ch or {}).get("name")
        for s in character_scores:
            if s.get("agent_key") == agent_key:
                char_score = s
                break
            if role_name and s.get("role_name") == role_name:
                char_score = s
                break

        gene_result = _agent_self_reflect_gene(session_id, agent_key, char_score, ctx)
        if "error" in gene_result:
            errors.append(f"{agent_key}: {gene_result['error']}")
            continue

        gene_id = gene_result["gene_id"]
        gene_full = get_gene(gene_id) or {"gene_id": gene_id, **gene_result}
        gene_full["gene_id"] = gene_id
        gene_full["id"] = gene_id
        gene_full["agent_key"] = agent_key
        gene_full["agent_name"] = agent.name
        genes.append(gene_full)

        cap_result = _build_capsule_display_for_gene(gene_id, agent_key, agent.name)
        if cap_result.get("id") or cap_result.get("title"):
            capsules.append(cap_result)
        elif "error" in cap_result:
            errors.append(f"Gene {gene_id}: {cap_result.get('error')}")

    review_bundle = {
        "session_id": session_id,
        "script_id": ctx.get("script_id"),
        "script_title": ctx.get("script_title"),
        "truth_killer": ctx.get("truth_killer"),
        "truth_review": truth_review,
        "character_scores": character_scores,
        "score_dimensions": SCORE_DIMENSIONS,
        "genes": genes,
        "capsules": capsules,
        "evolution_summary": {
            "genes_created": len(genes),
            "capsules_created": len(capsules),
            "capsules_stored": sum(1 for c in capsules if c.get("stored_in_db")),
            "errors": errors,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    persist_review_bundle(session_id, review_bundle, review_status="completed")
    return _finalize_review_bundle(review_bundle, session_id)


def persist_review_bundle(
    session_id: str,
    review_bundle: dict,
    review_status: str = "completed",
) -> None:
    """将复盘包写入内存与 game_sessions.result（即使游戏不在内存中也落库）。"""
    from api.agents.game_engine import game_engine
    from api.db.models import get_session, GameSession

    game = game_engine.get_game(session_id)
    if game:
        game["dm_review"] = review_bundle
        game_engine._sync_to_db(game)

    db = get_session()
    try:
        gs = db.query(GameSession).filter(
            GameSession.session_id == session_id
        ).first()
        if not gs:
            return
        result = dict(gs.result or {})
        result["dm_review"] = review_bundle
        result["review_status"] = review_status
        gs.result = result
        db.commit()
    except Exception as exc:
        db.rollback()
        logger.error(f"持久化复盘包失败 session={session_id}: {exc}")
    finally:
        db.close()


def mark_review_generating(session_id: str) -> None:
    """标记复盘生成中，供前端轮询。"""
    from api.db.models import get_session, GameSession

    db = get_session()
    try:
        gs = db.query(GameSession).filter(GameSession.session_id == session_id).first()
        if not gs:
            return
        result = dict(gs.result or {})
        result["review_status"] = "generating"
        gs.result = result
        db.commit()
    finally:
        db.close()


def _load_review_from_db(session_id: str) -> tuple[dict | None, str]:
    from api.db.models import get_session, GameSession

    db = get_session()
    try:
        gs = db.query(GameSession).filter(GameSession.session_id == session_id).first()
        if not gs or not gs.result:
            return None, ""
        return gs.result.get("dm_review"), gs.result.get("review_status") or ""
    finally:
        db.close()


def _orchestrator_key_from_node_id(node_id: str) -> str:
    """将 DB agent node id 解析为 orchestrator agent key。"""
    from api.orchestrator import orchestrator

    if not node_id:
        return ""
    for ok, agent in orchestrator.agents.items():
        if agent.node_id == node_id:
            return ok
        db_id = _resolve_agent_db_id(agent.node_id)
        if db_id == node_id:
            return ok
    return ""


def _enrich_gene_for_review(gene: dict) -> dict:
    """统一复盘页 Gene 字段，便于与 Capsule 关联。"""
    enriched = dict(gene)
    gene_id = enriched.get("gene_id") or enriched.get("id") or ""
    if gene_id:
        enriched["gene_id"] = gene_id
        enriched["id"] = gene_id
    if not enriched.get("agent_key"):
        node_id = enriched.get("agentNodeId") or enriched.get("agent_node_id") or ""
        enriched["agent_key"] = _orchestrator_key_from_node_id(node_id)
    if not enriched.get("agent_name") and enriched.get("agent_key"):
        from api.orchestrator import orchestrator
        agent = orchestrator.agents.get(enriched["agent_key"])
        if agent:
            enriched["agent_name"] = agent.name
    return enriched


def _hydrate_review_capsules(bundle: dict, session_id: str) -> dict:
    """补全复盘包中缺失的胶囊（从 gene.capsuleId 或预览生成）。"""
    from api.capsules.capsule_service import get_capsule, get_gene

    genes = [_enrich_gene_for_review(g) for g in (bundle.get("genes") or [])]
    bundle["genes"] = genes
    capsules = list(bundle.get("capsules") or [])
    covered_gene_ids = {
        c.get("geneId") for c in capsules if c.get("geneId")
    }

    for gene in genes:
        gene_id = gene.get("gene_id") or gene.get("id") or ""
        if not gene_id or gene_id in covered_gene_ids:
            continue

        agent_key = gene.get("agent_key") or ""
        agent_name = gene.get("agent_name") or ""
        capsule_id = gene.get("capsuleId") or gene.get("capsule_id")

        if capsule_id:
            stored = get_capsule(capsule_id) or {}
            if stored:
                title = stored.get("title") or ""
                if not title or "通用经验" in title or title.lower().startswith("companion"):
                    title = (gene.get("summary") or "").strip() or f"{agent_name} 本局经验胶囊"
                capsules.append({
                    **stored,
                    "title": title,
                    "agent_key": agent_key,
                    "agent_name": agent_name or stored.get("publisherRole") or "",
                    "geneId": gene_id,
                    "stored_in_db": True,
                })
                covered_gene_ids.add(gene_id)
                continue

        cap = _build_capsule_display_for_gene(gene_id, agent_key, agent_name)
        if cap.get("id") or cap.get("title"):
            cap["geneId"] = gene_id
            capsules.append(cap)
            covered_gene_ids.add(gene_id)
        elif gene_id:
            full = get_gene(gene_id) or gene
            capsules.append({
                "id": f"preview_{gene_id}",
                "geneId": gene_id,
                "agent_key": agent_key,
                "agent_name": agent_name,
                "title": full.get("summary") or f"{agent_name or 'Agent'} 本局经验胶囊",
                "category": full.get("category"),
                "content": full.get("detail") or full.get("summary") or "",
                "strategy": full.get("dmSuggestions") or "",
                "score": full.get("dmScore") or full.get("score") or 0.6,
                "stored_in_db": False,
                "reviewStatus": "preview",
            })
            covered_gene_ids.add(gene_id)

    bundle["capsules"] = capsules
    summary = dict(bundle.get("evolution_summary") or {})
    summary["genes_created"] = len(genes)
    summary["capsules_created"] = len(capsules)
    summary["capsules_stored"] = sum(1 for c in capsules if c.get("stored_in_db"))
    bundle["evolution_summary"] = summary
    return bundle


def _rebuild_review_bundle_from_db(session_id: str) -> dict | None:
    """cast/复盘包缺失时，从 GeneRecord 重建基因与胶囊列表（仅本局参与 Agent）。"""
    from api.capsules.capsule_service import get_gene
    from api.agents.game_engine import game_engine
    from api.db.models import get_session, GeneRecord
    from api.orchestrator import orchestrator

    game = game_engine.get_game(session_id) or {}
    ctx = _gather_session_context(session_id)
    agent_keys = _session_companion_agent_keys(game, session_id, ctx)
    allowed_node_ids: set[str] = set()
    for key in agent_keys:
        agent = orchestrator.agents.get(key)
        if not agent:
            continue
        if agent.node_id:
            allowed_node_ids.add(agent.node_id)
        db_id = _resolve_agent_db_id(agent.node_id)
        if db_id:
            allowed_node_ids.add(db_id)

    db = get_session()
    try:
        rows = (
            db.query(GeneRecord)
            .filter(GeneRecord.session_id == session_id)
            .order_by(GeneRecord.created_at.asc())
            .all()
        )
    finally:
        db.close()

    if not rows:
        return None

    if allowed_node_ids:
        rows = [r for r in rows if r.agent_node_id in allowed_node_ids]

    latest_by_agent: dict[str, GeneRecord] = {}
    for row in rows:
        latest_by_agent[row.agent_node_id] = row
    rows = list(latest_by_agent.values())

    if not rows:
        return None

    genes = [_enrich_gene_for_review(get_gene(row.id) or {"id": row.id, "gene_id": row.id}) for row in rows]
    bundle = {
        "session_id": session_id,
        "script_id": ctx.get("script_id"),
        "script_title": ctx.get("script_title"),
        "truth_killer": ctx.get("truth_killer"),
        "genes": genes,
        "capsules": [],
        "evolution_summary": {"genes_created": len(genes), "capsules_created": 0, "capsules_stored": 0},
        "review_status": "rebuilt",
    }
    return _hydrate_review_capsules(bundle, session_id)


def _finalize_review_bundle(bundle: dict, session_id: str) -> dict:
    bundle = _hydrate_review_capsules(bundle, session_id)
    if bundle.get("character_scores"):
        bundle["character_scores"] = _filter_character_scores(bundle["character_scores"])
    return bundle


def get_review_bundle(session_id: str) -> dict:
    """获取复盘数据（内存 / 数据库缓存，否则提示未生成）。"""
    from api.agents.game_engine import game_engine

    game = game_engine.get_game(session_id)
    if game and game.get("dm_review"):
        return {"success": True, **_finalize_review_bundle(dict(game["dm_review"]), session_id)}

    review, status = _load_review_from_db(session_id)
    if review:
        bundle = {"success": True, **_finalize_review_bundle({**review, "review_status": status}, session_id)}
        return bundle

    if status == "generating":
        return {
            "success": False,
            "message": "review_generating",
            "session_id": session_id,
            "review_status": "generating",
        }

    rebuilt = _rebuild_review_bundle_from_db(session_id)
    if rebuilt:
        return {"success": True, **rebuilt}

    return {"success": False, "message": "review_not_generated", "session_id": session_id}


def inject_all_capsules_for_agents() -> dict:
    """为所有已注册 Agent 注入全部历史胶囊（开局前调用）。"""
    from api.orchestrator import orchestrator

    injected = []
    for key, agent in orchestrator.agents.items():
        if not agent.registered or not agent.node_id:
            continue
        db_id = _resolve_agent_db_id(agent.node_id) or agent.node_id
        prompt = load_all_capsules_prompt(db_id, agent.role.value)
        if prompt and prompt not in (agent.constitution or ""):
            agent.constitution = (agent.constitution or "") + prompt
            injected.append(key)
    return {"success": True, "injected": injected, "count": len(injected)}


def _parse_json(text: str) -> dict:
    json_str = (text or "").strip()
    if "```json" in json_str:
        json_str = json_str.split("```json")[1].split("```")[0].strip()
    elif "```" in json_str:
        json_str = json_str.split("```")[1].split("```")[0].strip()
    return json.loads(json_str)


def load_all_capsules_prompt(agent_node_id: str, agent_role: str) -> str:
    """加载某 Agent 的全部已批准胶囊，合并为 prompt。"""
    from api.db.models import get_session, CapsuleRecord

    db = get_session()
    try:
        all_caps = db.query(CapsuleRecord).filter(
            CapsuleRecord.review_status == "approved",
        ).order_by(CapsuleRecord.score.desc()).all()

        matched = []
        for c in all_caps:
            roles = c.applicable_roles or []
            if agent_node_id and c.publisher_id == agent_node_id:
                matched.append(c)
            elif agent_role in roles:
                matched.append(c)

        if not matched:
            return ""

        parts = ["\n\n## 历史经验胶囊（本局前全部注入）"]
        for c in matched:
            c.usage_count = (c.usage_count or 0) + 1
            parts.append(f"\n### {c.title}（评分 {c.score:.2f}）")
            parts.append(c.content or "")
            if c.strategy:
                parts.append(f"策略：{c.strategy}")
            if c.anti_patterns:
                parts.append(f"避免：{c.anti_patterns}")
        db.commit()
        return "\n".join(parts)
    except Exception as e:
        logger.error(f"load_all_capsules_prompt failed: {e}")
        db.rollback()
        return ""
    finally:
        db.close()
