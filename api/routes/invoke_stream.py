"""
EvoMap Murder Game - Streaming AI Invocation Routes

流式响应：使用 Server-Sent Events (SSE) 实时返回 AI 回复。
简化版：直接流式调用 LLM，不做 critique/refine 安全检查。
前端可通过 EventSource 或 fetch + ReadableStream 消费。
"""

import json
import logging
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from api.schemas.invoke_types import InvocationRequest
from api.llm.llm_service import ROLE_SYSTEM_PROMPTS
from api.agents.game_engine import game_engine

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/stream")
async def invoke_ai_stream(req: InvocationRequest):
    """流式调用 AI 生成回复（SSE 格式）。

    简化版：直接流式调用 LLM，没有 critique/refine 检查。
    返回 text/event-stream，每条事件格式：
        data: {"type": "token", "content": "..."}\n\n
        data: {"type": "done", "final": "..."}\n\n
    """
    role = req.actor.role_type or "companion"
    system_prompt = ROLE_SYSTEM_PROMPTS.get(role, ROLE_SYSTEM_PROMPTS["companion"])

    # 将角色信息融入 system prompt
    system_prompt += f"\n\n当前角色：{req.actor.name}\n角色简介：{req.actor.bio}\n性格：{req.actor.personality}"

    if req.actor.secret:
        system_prompt += f"\n角色秘密（仅你自己知道）：{req.actor.secret}"

    if req.actor.violation:
        system_prompt += f"\n行为限制（绝不能违反）：{req.actor.violation}"

    # 构建用户消息
    user_message = ""
    for msg in req.chat_messages:
        user_message += f"{msg.role}: {msg.content}\n"

    # 记录对话计数
    if req.session_id:
        game_engine.record_chat(req.session_id)

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
