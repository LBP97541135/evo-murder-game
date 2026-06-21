"""
EvoMap Murder Game - AI Invocation Routes

三层管道调用：respond_initial → critique → refine。
v2.2 集成 game_engine：根据游戏阶段、Agent 记忆和证物动态调整 prompt。
"""

import json
import logging
from fastapi import APIRouter

from api.schemas.invoke_types import InvocationRequest, InvocationResponse
from api.llm.llm_service import invoke_with_pipeline, ROLE_SYSTEM_PROMPTS
from api.agents.game_engine import game_engine, GamePhase, PHASE_CONFIG

logger = logging.getLogger(__name__)

router = APIRouter()


def _build_game_context_prompt(session_id: str, actor_name: str) -> str:
    """从 game_engine 读取当前游戏状态，构建环境上下文 prompt 片段。

    注入信息：
      - 当前游戏阶段及阶段描述
      - 该 Agent 的压缩记忆和关键事实
      - 已发现的证物
      - 全局故事背景
      - 全局 phase_prompt
    """
    game = game_engine.get_game(session_id)
    if not game:
        return ""

    phase = game.get("current_phase", "")
    phase_config = PHASE_CONFIG.get(GamePhase(phase)) if phase else None
    agent_state = game.get("agents", {}).get(actor_name)

    parts = []

    # 阶段信息
    if phase_config:
        parts.append(
            f"【当前游戏阶段】{phase_config['display_name']}\n{phase_config['description']}\n"
            f"阶段指引：{phase_config['phase_prompt']}"
        )
    else:
        parts.append(f"【当前游戏阶段】{phase}")

    # Agent 记忆
    if agent_state:
        if agent_state.compressed_summary:
            parts.append(f"【记忆摘要】{agent_state.compressed_summary}")
        if agent_state.key_facts:
            parts.append(f"【已确认的关键事实】\n" + "\n".join(f"- {f}" for f in agent_state.key_facts[-5:]))
        if agent_state.discovered_evidences:
            ev_lines = []
            for ev in agent_state.discovered_evidences[-8:]:
                ev_lines.append(f"- {ev.get('name', '?')}: {ev.get('description', '')}")
            parts.append("【已发现的证物】\n" + "\n".join(ev_lines))

    return "\n\n".join(parts)


@router.post("/", response_model=InvocationResponse)
async def invoke_ai(req: InvocationRequest):
    """调用 AI 生成回复（三层管道：initial → critique → refine）。

    当传入 session_id 时，自动注入游戏阶段、Agent 记忆和证物上下文。
    """
    role = req.actor.role_type or "companion"
    system_prompt = ROLE_SYSTEM_PROMPTS.get(role, ROLE_SYSTEM_PROMPTS["companion"])

    # 将角色信息融入 system prompt
    system_prompt += f"\n\n当前角色：{req.actor.name}\n角色简介：{req.actor.bio}\n性格：{req.actor.personality}"

    if req.actor.secret:
        system_prompt += f"\n角色秘密（仅你自己知道）：{req.actor.secret}"

    if req.actor.violation:
        system_prompt += f"\n行为限制（绝不能违反）：{req.actor.violation}"

    # 注入游戏环境上下文（如果提供了 session_id）
    if req.session_id:
        game_context = _build_game_context_prompt(req.session_id, req.actor.name)
        if game_context:
            system_prompt += f"\n\n---\n{game_context}"

    # 构建用户消息
    user_message = ""
    for msg in req.chat_messages:
        user_message += f"{msg.role}: {msg.content}\n"

    # 构建历史消息（Agent 的 chat_history，避免重复传）
    history = None
    if req.session_id:
        game = game_engine.get_game(req.session_id)
        if game:
            agent_state = game.get("agents", {}).get(req.actor.name)
            if agent_state and agent_state.chat_history:
                # 只取最近 10 条作为上下文
                history = agent_state.chat_history[-10:]

    # Critique 规则——防止剧透和违规
    critique_prompt = (
        "1. 回复不能包含角色秘密的直接泄露\n"
        "2. 回复不能包含未获得的线索\n"
        "3. 回复不能包含其他角色的私密信息\n"
        "4. 回复不能违背角色性格设定"
    )

    result = invoke_with_pipeline(
        system_prompt=system_prompt,
        user_message=user_message,
        history=history,
        critique_prompt=critique_prompt,
        skip_critique=False,
    )

    # ========== 自动保存对话记录（P0#2） ==========
    if req.session_id:
        _auto_save_conversation(req, result)

    return InvocationResponse(
        original=result["initial"],
        critique=result.get("critique", ""),
        refined=result.get("refined", ""),
        final_response=result["final"],
    )


def _auto_save_conversation(req: InvocationRequest, result: dict) -> None:
    """自动保存 invoke 结果到 conversation_turns 表并同步到 Agent 游戏状态。"""
    try:
        from api.db.models import get_session, ConversationTurn
        import uuid

        db_session = get_session()
        try:
            turn = ConversationTurn(
                id=f"turn_{uuid.uuid4().hex[:8]}",
                session_id=req.session_id,
                actor_name=req.actor.name,
                chat_messages=[m.model_dump() for m in req.chat_messages],
                original_response=result.get("initial", ""),
                critique_response=result.get("critique", ""),
                refined_response=result.get("refined", ""),
                final_response=result.get("final", ""),
            )
            db_session.add(turn)
            db_session.commit()

            # 同步到 Agent 游戏状态
            game_engine.add_chat_to_agent(
                game_id=req.session_id,
                agent_key=req.actor.name,
                role=req.actor.name,
                content=result.get("final", ""),
            )
            game_engine.record_chat(game_id=req.session_id)
        except Exception as db_err:
            logger.warning(f"自动保存对话失败（非致命）: {db_err}")
        finally:
            db_session.close()
    except Exception as e:
        logger.warning(f"自动保存对话模块加载失败（非致命）: {e}")
