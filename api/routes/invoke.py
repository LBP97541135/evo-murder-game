"""
EvoMap Murder Game - AI Invocation Routes

三层管道调用：respond_initial → critique → refine。
"""

from fastapi import APIRouter

from api.schemas.invoke_types import InvocationRequest, InvocationResponse
from api.llm.llm_service import invoke_with_pipeline, ROLE_SYSTEM_PROMPTS

router = APIRouter()


@router.post("/", response_model=InvocationResponse)
async def invoke_ai(req: InvocationRequest):
    """调用 AI 生成回复（三层管道：initial → critique → refine）。"""
    role = req.actor.role_type or "companion"
    system_prompt = ROLE_SYSTEM_PROMPTS.get(role, ROLE_SYSTEM_PROMPTS["companion"])

    # 将角色信息融入 system prompt
    system_prompt += f"\n\n当前角色：{req.actor.name}\n角色简介：{req.actor.bio}\n性格：{req.actor.personality}"

    if req.actor.secret:
        system_prompt += f"\n角色秘密（仅你自己知道）：{req.actor.secret}"

    # 构建用户消息
    user_message = ""
    for msg in req.chat_messages:
        user_message += f"{msg.role}: {msg.content}\n"

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
        critique_prompt=critique_prompt,
        skip_critique=False,
    )

    return InvocationResponse(
        original=result["initial"],
        critique=result.get("critique", ""),
        refined=result.get("refined", ""),
        final_response=result["final"],
    )
