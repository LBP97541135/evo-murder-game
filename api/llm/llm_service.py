"""
EvoMap Murder Game - LLM Service

三层 AI 管道：respond_initial → critique → refine
支持多推理服务商：Anthropic / OpenAI / Groq / OpenRouter / Ollama
从 ai-murder-mystery 复用核心架构，适配多Agent协作场景。
"""

import json
import logging
from typing import Optional

from api.config.settings import (
    INFERENCE_SERVICE, MODEL, MAX_TOKENS, API_KEY,
    OLLAMA_URL, GROQ_API_BASE, OPENROUTER_API_BASE, OPENAI_API_BASE,
    EVOMAP_LLM_BASE_URL, EVOMAP_LLM_API_KEY,
)

logger = logging.getLogger(__name__)


# ============================
# 角色类型与 Prompt 模板
# ============================

ROLE_SYSTEM_PROMPTS = {
    "dm": (
        "你是剧本杀的主持人（DM-Agent）。你掌握完整真相和所有角色秘密。\n"
        "你的职责是引导游戏流程、控制节奏、发放线索、组织投票。\n"
        "你绝不直接泄露答案，只通过分级提示帮助玩家。\n"
        "你的说话风格根据 constitution 决定。\n"
    ),
    "companion": (
        "你是剧本杀中的角色扮演Agent。你正在扮演一个剧本角色。\n"
        "你只能使用角色已知的信息，绝不能泄露角色秘密或未获得的线索。\n"
        "你的人设（constitution）决定你的表演风格，角色设定决定你演谁。\n"
        "你对其他角色的态度取决于角色关系设定。\n"
    ),
    "assistant": (
        "你是个人助手Agent，不参与游戏角色扮演。\n"
        "你专注于理解用户偏好、生成画像标签、推荐剧本和阵容。\n"
        "你的推荐必须附带理由和依据。\n"
    ),
}


# ============================
# Agent 记忆压缩 & 意图生成 Prompt
# ============================

MEMORY_COMPRESSION_PROMPT = (
    "你是一个对话摘要专家。请将以下对话内容压缩为2-3句话的摘要，"
    "并列出最重要的3-5个关键事实（涉及的关键线索、人物关系变化、嫌疑指向等）。\n"
    "输出 JSON 格式：\n"
    '{{"summary": "2-3句话摘要", "key_facts": ["事实1", "事实2"]}}\n'
    "不要输出其他内容。"
)

INTENT_GENERATION_PROMPT = (
    "你是一个剧本杀 Agent，正在决定下一步行动。\n"
    "基于你的角色身份、当前记忆、已知证物和局势，你需要判断：\n"
    "1. 是否想插队发言（interject）？——你是否有紧急信息要说？\n"
    "2. 是否想发起私聊（private_chat）？——你想悄悄和谁说什么？\n"
    "3. 是否想出示证物（present_evidence）？——你想把某个证物给谁看？\n"
    "\n"
    "注意：喊话（callout）是在发言阶段直接对某个 Agent 提问，不需要单独意图。\n"
    "\n"
    "请输出 JSON 格式，没有意图的字段设为 null：\n"
    '{{"interject": {{"reason": "...", "urgency": "low|medium|high"}} or null, '
    '"private_chat": {{"target": "对方名字", "topic": "想说什么"}} or null, '
    '"present_evidence": {{"evidence_id": "...", "target": "给谁看", "reason": "为什么"}} or null}}\n'
)

AGENT_CHAT_BUILDER_PROMPT = (
    "根据以下信息生成你的发言：\n"
    "- 你的角色身份和秘密\n"
    "- 当前游戏阶段\n"
    "- 上一阶段的摘要和关键事实\n"
    "- 当前阶段的对话记录\n"
    "- 你已发现的证物\n"
    "\n"
    "请以角色身份自然发言。如果是被喊话，先回答对方的提问。\n"
    "如需出示证物、喊话其他 Agent 或发起私聊，请在发言末尾附加行动标记。"
)


def get_provider_base_url(service: str) -> str:
    """根据推理服务类型返回 API base URL。"""
    urls = {
        "anthropic": "https://api.anthropic.com",
        "openai": OPENAI_API_BASE,
        "groq": GROQ_API_BASE,
        "openrouter": OPENROUTER_API_BASE,
        "ollama": OLLAMA_URL,
    }
    return urls.get(service, OPENAI_API_BASE)


# ============================
# 三层 AI 管道
# ============================

def respond_initial(
    system_prompt: str,
    user_message: str,
    history: list = None,
    model: str = MODEL,
    temperature: float = 0.7,
    max_tokens: int = MAX_TOKENS,
    service: str = INFERENCE_SERVICE,
    api_key: str = API_KEY,
) -> str:
    """第一层：生成初始 AI 回复。"""
    messages = []
    if history:
        for h in history:
            messages.append({"role": h.get("role", "user"), "content": h.get("content", "")})
    messages.append({"role": "user", "content": user_message})

    try:
        if service == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=model, max_tokens=max_tokens,
                system=system_prompt, messages=messages, temperature=temperature,
            )
            return response.content[0].text

        elif service in ("openai", "groq", "openrouter"):
            from openai import OpenAI
            base_url = get_provider_base_url(service)
            client = OpenAI(base_url=base_url, api_key=api_key)
            response = client.chat.completions.create(
                model=model, max_tokens=max_tokens,
                messages=[{"role": "system", "content": system_prompt}] + messages,
                temperature=temperature,
            )
            return response.choices[0].message.content

        elif service == "ollama":
            import httpx
            url = f"{OLLAMA_URL}/api/chat"
            payload = {
                "model": model, "messages": messages,
                "system": system_prompt, "stream": False,
                "options": {"temperature": temperature},
            }
            r = httpx.post(url, json=payload, timeout=120.0)
            return r.json().get("message", {}).get("content", "")

        else:
            logger.warning(f"Unknown inference service: {service}, falling back to OpenAI")
            from openai import OpenAI
            client = OpenAI(base_url=OPENAI_API_BASE, api_key=api_key)
            response = client.chat.completions.create(
                model=model, max_tokens=max_tokens,
                messages=[{"role": "system", "content": system_prompt}] + messages,
                temperature=temperature,
            )
            return response.choices[0].message.content

    except Exception as e:
        logger.error(f"LLM invoke failed (service={service}, model={model}): {e}")
        return f"[AI Error] {str(e)}"


def critique(
    initial_response: str,
    critique_prompt: str,
    model: str = MODEL,
    max_tokens: int = 1024,
    service: str = INFERENCE_SERVICE,
    api_key: str = API_KEY,
) -> str:
    """第二层：批评检查，检查回复是否违反规则。"""
    system = (
        "你是AI回复质量审查员。你的任务是检查以下回复是否违反指定原则。\n"
        "如果没有任何违规，回复 'NONE'。\n"
        "如果有违规，指出具体违规内容和原因。\n"
    )
    user = f"审查原则：{critique_prompt}\n\n待审查的回复：\n{initial_response}"

    return respond_initial(
        system_prompt=system, user_message=user,
        model=model, temperature=0.3, max_tokens=max_tokens,
        service=service, api_key=api_key,
    )


def refine(
    initial_response: str,
    critique_result: str,
    system_prompt: str,
    user_message: str,
    model: str = MODEL,
    max_tokens: int = MAX_TOKENS,
    service: str = INFERENCE_SERVICE,
    api_key: str = API_KEY,
) -> str:
    """第三层：根据批评结果修订回复。"""
    refine_prompt = (
        f"你之前生成了以下回复，但审查发现存在问题：\n"
        f"原回复：{initial_response}\n\n"
        f"审查结果：{critique_result}\n\n"
        f"请根据审查意见修订你的回复，确保不再违反规则。保持语气和风格一致。\n"
        f"原始用户消息：{user_message}"
    )
    return respond_initial(
        system_prompt=system_prompt, user_message=refine_prompt,
        model=model, temperature=0.7, max_tokens=max_tokens,
        service=service, api_key=api_key,
    )


def check_whether_to_refine(critique_result: str) -> bool:
    """检查批评结果是否包含违规（即是否需要 refine）。NONE = 无需修订。"""
    return "NONE" not in critique_result.upper()


def invoke_with_pipeline(
    system_prompt: str,
    user_message: str,
    history: list = None,
    critique_prompt: str = "",
    model: str = MODEL,
    temperature: float = 0.7,
    max_tokens: int = MAX_TOKENS,
    service: str = INFERENCE_SERVICE,
    api_key: str = API_KEY,
    skip_critique: bool = False,
) -> dict:
    """完整三层管道调用：initial → critique → refine（如果需要）。

    Returns:
        {
            "initial": str,           # 原始回复
            "critique": str | None,   # 批评结果
            "refined": str | None,    # 修订后回复
            "final": str,             # 最终输出
        }
    """
    initial = respond_initial(
        system_prompt, user_message, history,
        model, temperature, max_tokens, service, api_key,
    )

    if skip_critique or not critique_prompt:
        return {"initial": initial, "critique": None, "refined": None, "final": initial}

    critique_result = critique(initial, critique_prompt, model, 1024, service, api_key)

    if not check_whether_to_refine(critique_result):
        return {"initial": initial, "critique": critique_result, "refined": None, "final": initial}

    refined = refine(initial, critique_result, system_prompt, user_message, model, max_tokens, service, api_key)
    return {"initial": initial, "critique": critique_result, "refined": refined, "final": refined}
