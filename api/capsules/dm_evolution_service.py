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
        elif entry.get("type") == "human":
            participants.append({
                "role_name": entry.get("role", ""),
                "agent_key": "user",
                "type": "human",
            })

    player_role = game.get("player_character_name", "")
    if player_role and not any(p["role_name"] == player_role for p in participants):
        participants.append({"role_name": player_role, "agent_key": "user", "type": "human"})

    from api.orchestrator import orchestrator

    for _key, state in game.get("agents", {}).items():
        agent = orchestrator.agents.get(_key)
        if agent and agent.role.value == "dm":
            continue
        rn = (state.character or {}).get("name", "")
        if rn and not any(p["role_name"] == rn for p in participants):
            participants.append({"role_name": rn, "agent_key": _key, "type": "agent"})

    def _is_review_participant(p: dict) -> bool:
        role_name = p.get("role_name", "")
        if role_name in ("侦探", "DM", "雾港主理人"):
            return False
        agent_key = p.get("agent_key", "")
        if agent_key and agent_key not in ("user", ""):
            agent = orchestrator.agents.get(agent_key)
            if agent and agent.role.value == "dm":
                return False
        return bool(role_name)

    participants = [p for p in participants if _is_review_participant(p)]

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
    return results


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


def _session_companion_agent_keys(game: dict) -> list[str]:
    """本局参与复盘自进化的 Agent：仅陪玩 companion，不含 DM。"""
    from api.orchestrator import orchestrator

    keys: list[str] = []
    for entry in game.get("cast") or []:
        if entry.get("type") != "agent":
            continue
        agent_key = entry.get("agentKey") or entry.get("agent_key")
        if not agent_key:
            continue
        agent = orchestrator.agents.get(agent_key)
        if not agent or not agent.registered or agent.role.value == "dm":
            continue
        if agent_key not in keys:
            keys.append(agent_key)

    if keys:
        return keys

    return [
        k for k, a in orchestrator.agents.items()
        if a.registered and a.role.value == "companion"
    ]


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

    agent_keys = _session_companion_agent_keys(game)

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

    game = game_engine.get_game(session_id)
    if game:
        game["dm_review"] = review_bundle
        game_engine._sync_to_db(game)

    return review_bundle


def get_review_bundle(session_id: str) -> dict:
    """获取复盘数据（优先缓存，否则提示未生成）。"""
    from api.agents.game_engine import game_engine

    game = game_engine.get_game(session_id)
    if game and game.get("dm_review"):
        return {"success": True, **game["dm_review"]}

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
