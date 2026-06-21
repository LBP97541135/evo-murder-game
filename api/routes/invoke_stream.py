"""
EvoMap Murder Game - Streaming AI Invocation Routes

流式响应：使用 Server-Sent Events (SSE) 实时返回 AI 回复。
v2.2 集成 game_engine：根据游戏阶段、Agent 记忆和证物动态调整 prompt。
前端可通过 EventSource 或 fetch + ReadableStream 消费。
"""

import json
import uuid
import logging
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from api.schemas.invoke_types import InvocationRequest
from api.agents.game_engine import game_engine
from api.agents.game_context import build_invoke_system_prompt, find_agent_key

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/stream")
async def invoke_ai_stream(req: InvocationRequest):
    """流式调用 AI 生成回复（SSE 格式）。

    当传入 session_id 时，自动注入游戏阶段、Agent 记忆和证物上下文。
    流式完成后自动保存对话记录。
    返回 text/event-stream，每条事件格式：
        data: {"type": "token", "content": "..."}\n\n
        data: {"type": "done", "final": "..."}\n\n
    """
    role = req.actor.role_type or "companion"
    system_prompt = build_invoke_system_prompt(
        session_id=req.session_id,
        actor_name=req.actor.name,
        role_type=role,
        bio=req.actor.bio or "",
        personality=req.actor.personality or "",
        secret=req.actor.secret or "",
        violation=req.actor.violation or "",
        speech_phase=req.speech_phase or None,
    )

    # 构建用户消息
    user_message = ""
    for msg in req.chat_messages:
        user_message += f"{msg.role}: {msg.content}\n"

    def event_generator():
        """SSE 事件生成器。"""
        try:
            from api.config.settings import INFERENCE_SERVICE, MODEL, MAX_TOKENS, API_KEY, OPENAI_API_BASE

            messages = [{"role": "system", "content": system_prompt}]
            for msg in req.chat_messages:
                messages.append({"role": msg.role, "content": msg.content})

            full_response = ""

            if INFERENCE_SERVICE in ("openai", "groq", "openrouter"):
                from openai import OpenAI
                base_url = OPENAI_API_BASE if INFERENCE_SERVICE == "openai" else (
                    "https://api.groq.com/openai/v1" if INFERENCE_SERVICE == "groq" else
                    "https://openrouter.ai/api/v1"
                )
                client = OpenAI(base_url=base_url, api_key=API_KEY)

                stream = client.chat.completions.create(
                    model=MODEL,
                    max_tokens=MAX_TOKENS,
                    messages=messages,
                    temperature=req.temperature,
                    stream=True,
                )

                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        token = chunk.choices[0].delta.content
                        full_response += token
                        yield f"data: {json.dumps({'type': 'token', 'content': token}, ensure_ascii=False)}\n\n"

            else:
                # 不直接支持流式的服务，用非流式然后模拟逐字输出
                from api.llm.llm_service import respond_initial
                full_response = respond_initial(
                    system_prompt=system_prompt,
                    user_message=user_message,
                    temperature=req.temperature,
                )
                chunk_size = 4
                for i in range(0, len(full_response), chunk_size):
                    token = full_response[i:i + chunk_size]
                    yield f"data: {json.dumps({'type': 'token', 'content': token}, ensure_ascii=False)}\n\n"

            # ========== 自动保存对话记录（P0#2） ==========
            if req.session_id:
                try:
                    from api.db.models import get_session, ConversationTurn

                    db_session = get_session()
                    try:
                        # 查找正确的 agent_key 用于记录同步
                        _game = game_engine.get_game(req.session_id)
                        _agent_key = find_agent_key(_game, req.actor.name) if _game else None

                        turn = ConversationTurn(
                            id=f"turn_{uuid.uuid4().hex[:8]}",
                            session_id=req.session_id,
                            # 存储时 actor_name 保持为角色名，方便前端查询
                            actor_name=req.actor.name,
                            chat_messages=[m.model_dump() for m in req.chat_messages],
                            original_response=full_response,
                            critique_response="",
                            refined_response="",
                            final_response=full_response,
                        )
                        db_session.add(turn)
                        db_session.commit()

                        # 同步到 Agent 游戏状态
                        if _agent_key:
                            game_engine.add_chat_to_agent(
                                game_id=req.session_id,
                                agent_key=_agent_key,
                                role=req.actor.name,
                                content=full_response,
                            )
                            game_engine.record_chat(game_id=req.session_id)
                    except Exception as db_err:
                        logger.warning(f"流式自动保存对话失败（非致命）: {db_err}")
                    finally:
                        db_session.close()
                except Exception as e:
                    logger.warning(f"流式自动保存模块加载失败（非致命）: {e}")

            # 流式完成后发送 done 事件
            yield f"data: {json.dumps({'type': 'done', 'final': full_response}, ensure_ascii=False)}\n\n"

        except Exception as e:
            logger.error(f"流式调用失败: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
