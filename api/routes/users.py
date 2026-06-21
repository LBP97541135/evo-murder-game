"""
EvoMap Murder Game - User Profile & Assistant Routes

用户画像与个人助手中枢 API。
"""

import uuid
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from api.db.models import get_session, UserProfile
from api.agents.agent_persona_service import get_persona_by_key

logger = logging.getLogger(__name__)

router = APIRouter()

COMPASS_PERSONA_KEY = "compass"

COMPASS_GREETING = (
    "你好，我是指南针，你的进化酒馆个人助手。\n\n"
    "我可以帮你：\n"
    "1. 根据你的偏好画像推荐剧本、难度和时长\n"
    "2. 搭配适合的 Agent 阵容（DM / 陪玩 / 助手）\n"
    "3. 解答游戏规则、流程和 Agent 能力\n"
    "4. 给出开局前的准备建议\n\n"
    "你可以直接问我，例如：\n"
    "·「推荐一个适合新手的推理本」\n"
    "·「锈铁大道适合一个人观战吗？」\n"
    "·「白鸦和月蛾有什么区别？」\n\n"
    "我会根据你的画像给出有依据、可落地的建议。我们从哪开始？"
)


class ProfileUpdateRequest(BaseModel):
    display_name: Optional[str] = None
    preferred_genres: Optional[list[str]] = None
    preferred_difficulty: Optional[str] = None
    preferred_duration: Optional[str] = None
    tags: Optional[list[str]] = None
    profile_data: Optional[dict] = None
    total_games: Optional[int] = None
    total_hours: Optional[int] = None
    completed_games: Optional[int] = None
    favorite_agents: Optional[list[str]] = None


class AssistantChatRequest(BaseModel):
    message: str


class AssistantChatResponse(BaseModel):
    reply: str


def _load_compass_persona() -> dict:
    persona = get_persona_by_key(COMPASS_PERSONA_KEY)
    if persona:
        return persona
    return {
        "key": COMPASS_PERSONA_KEY,
        "name": "指南针",
        "personaText": "你是指南针，进化酒馆的个人助手，不参与游戏角色扮演。",
        "speechStyle": "专业但不冰冷，有条理，分点陈述。",
        "backstory": "",
        "values": ["数据驱动", "用户至上"],
        "antiPatterns": ["不参与游戏角色扮演", "不泄露其他用户信息"],
    }


def _build_compass_system_prompt(profile: UserProfile, scripts_str: str, persona: dict) -> str:
    genius = "、".join(persona.get("genius") or []) or "推荐引擎、用户画像"
    values = "、".join(persona.get("values") or []) or "用户至上"
    anti = "、".join(persona.get("antiPatterns") or []) or "不参与游戏、不剧透"

    return (
        f"你是{persona.get('name', '指南针')}，进化酒馆的个人助手 Agent。\n\n"
        f"【人设】\n{persona.get('personaText', '')}\n\n"
        f"【背景】\n{persona.get('backstory', '')}\n\n"
        f"【说话风格】\n{persona.get('speechStyle', '')}\n\n"
        f"【擅长】{genius}\n"
        f"【价值观】{values}\n"
        f"【禁止】{anti}\n\n"
        "你的职责：\n"
        "1. 基于用户画像推荐剧本、角色和 Agent 阵容\n"
        "2. 回答游戏规则、流程、Agent 能力相关问题\n"
        "3. 给出开局前准备建议\n"
        "4. 绝不参与剧本杀角色扮演，绝不剧透案件真相\n\n"
        f"【用户画像】\n"
        f"玩家等级：{profile.level}\n"
        f"偏好题材：{', '.join(profile.preferred_genres) if profile.preferred_genres else '未设置'}\n"
        f"偏好难度：{profile.preferred_difficulty or '未设置'}\n"
        f"偏好时长：{profile.preferred_duration or '未设置'}\n"
        f"系统标签：{', '.join(profile.tags) if profile.tags else '暂无'}\n"
        f"总游戏局数：{profile.total_games}\n"
        f"总游戏时长：{profile.total_hours} 小时\n\n"
        f"【可用剧本库】\n{scripts_str}\n\n"
        "请根据以上信息，用指南针的口吻友好、简洁地回答。推荐时说明理由。"
    )


# ============================
# 用户画像 CRUD
# ============================

def _get_or_create_profile(user_id: str = "user_default") -> UserProfile:
    """获取或创建用户画像。"""
    db_session = get_session()
    try:
        profile = db_session.query(UserProfile).filter(UserProfile.id == user_id).first()
        if not profile:
            profile = UserProfile(id=user_id)
            db_session.add(profile)
            db_session.commit()
            db_session.refresh(profile)
        return profile
    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db_session.close()


@router.get("/profile", response_model=dict)
async def get_profile(user_id: str = "user_default"):
    """获取用户画像数据。"""
    profile = _get_or_create_profile(user_id)
    return {
        "success": True,
        "profile": {
            "id": profile.id,
            "display_name": profile.display_name,
            "level": profile.level,
            "avatar_url": profile.avatar_url,
            "preferred_genres": profile.preferred_genres,
            "preferred_difficulty": profile.preferred_difficulty,
            "preferred_duration": profile.preferred_duration,
            "tags": profile.tags,
            "profile_data": profile.profile_data,
            "total_games": profile.total_games,
            "total_hours": profile.total_hours,
            "completed_games": profile.completed_games,
            "favorite_agents": profile.favorite_agents,
        },
    }


@router.post("/profile/update", response_model=dict)
async def update_profile(req: ProfileUpdateRequest, user_id: str = "user_default"):
    """更新用户画像数据。"""
    db_session = get_session()
    try:
        profile = db_session.query(UserProfile).filter(UserProfile.id == user_id).first()
        if not profile:
            profile = UserProfile(id=user_id)
            db_session.add(profile)

        if req.display_name is not None:
            profile.display_name = req.display_name
        if req.preferred_genres is not None:
            profile.preferred_genres = req.preferred_genres
        if req.preferred_difficulty is not None:
            profile.preferred_difficulty = req.preferred_difficulty
        if req.preferred_duration is not None:
            profile.preferred_duration = req.preferred_duration
        if req.tags is not None:
            profile.tags = req.tags
        if req.profile_data is not None:
            profile.profile_data = req.profile_data
        if req.total_games is not None:
            profile.total_games = req.total_games
        if req.total_hours is not None:
            profile.total_hours = req.total_hours
        if req.completed_games is not None:
            profile.completed_games = req.completed_games
        if req.favorite_agents is not None:
            profile.favorite_agents = req.favorite_agents

        db_session.commit()
        return {"success": True, "message": "画像已更新"}
    except Exception as e:
        db_session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db_session.close()


# ============================
# 个人助手 AI 问答（指南针人设）
# ============================

@router.get("/assistant/greeting")
async def assistant_greeting(user_id: str = "user_default"):
    """获取指南针初始引导话术与人设摘要。"""
    persona = _load_compass_persona()
    profile = _get_or_create_profile(user_id)
    genres = "、".join(profile.preferred_genres or []) or "尚未设置"
    greeting = COMPASS_GREETING
    if profile.preferred_genres:
        greeting += f"\n\n（我已读取你的偏好：{genres}，随时可以为你定制推荐。）"
    return {
        "success": True,
        "greeting": greeting,
        "persona": {
            "key": persona.get("key", COMPASS_PERSONA_KEY),
            "name": persona.get("name", "指南针"),
            "personaText": persona.get("personaText", ""),
            "speechStyle": persona.get("speechStyle", ""),
        },
    }


@router.post("/assistant/chat", response_model=AssistantChatResponse)
async def assistant_chat(req: AssistantChatRequest, user_id: str = "user_default"):
    """个人助手 AI 问答——使用数据库指南针人设与提示词。"""
    from api.llm.llm_service import respond_initial

    profile = _get_or_create_profile(user_id)
    persona = _load_compass_persona()

    from api.db.models import Script as ScriptModel
    db_session = get_session()
    try:
        scripts = db_session.query(ScriptModel).all()
        script_list = [
            f"「{s.title}」({s.genre}, {s.difficulty}, {s.duration}分钟)"
            for s in scripts
        ]
        scripts_str = "\n".join(script_list) if script_list else "暂无"
    finally:
        db_session.close()

    system_prompt = _build_compass_system_prompt(profile, scripts_str, persona)

    try:
        reply = respond_initial(
            system_prompt=system_prompt,
            user_message=req.message,
            temperature=0.7,
            max_tokens=1024,
        )
    except Exception as e:
        logger.error(f"Assistant chat failed: {e}")
        reply = "抱歉，我现在暂时无法回答，请稍后再试。"

    db_session = get_session()
    try:
        profile_db = db_session.query(UserProfile).filter(UserProfile.id == user_id).first()
        if profile_db:
            history = profile_db.assistant_chat_history or []
            history.append({"role": "user", "content": req.message})
            history.append({"role": "assistant", "content": reply})
            profile_db.assistant_chat_history = history[-20:]
            db_session.commit()
    except Exception:
        pass
    finally:
        db_session.close()

    return AssistantChatResponse(reply=reply)


@router.get("/assistant/history")
async def get_assistant_history(user_id: str = "user_default"):
    """获取个人助手对话历史。"""
    profile = _get_or_create_profile(user_id)
    return {
        "success": True,
        "history": profile.assistant_chat_history or [],
    }
