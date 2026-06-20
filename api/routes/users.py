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

logger = logging.getLogger(__name__)

router = APIRouter()


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
# 个人助手 AI 问答
# ============================

@router.post("/assistant/chat", response_model=AssistantChatResponse)
async def assistant_chat(req: AssistantChatRequest, user_id: str = "user_default"):
    """个人助手 AI 问答——基于用户画像和偏好提供推荐和回答。"""
    from api.llm.llm_service import respond_initial

    # 获取用户画像
    profile = _get_or_create_profile(user_id)

    # 从数据库获取剧本列表
    from api.db.models import Script as ScriptModel
    db_session = get_session()
    try:
        scripts = db_session.query(ScriptModel).all()
        script_list = []
        for s in scripts:
            script_list.append(f"「{s.title}」({s.genre}, {s.difficulty}, {s.duration}分钟)")
        scripts_str = "\n".join(script_list) if script_list else "暂无"
    finally:
        db_session.close()

    # 构建 system prompt
    system_prompt = (
        "你是进化酒馆的个人助手Agent，你的职责是：\n"
        "1. 基于用户的偏好画像推荐剧本\n"
        "2. 推荐适合的角色和陪玩Agent阵容\n"
        "3. 回答关于游戏、规则、Agent能力的问题\n"
        "4. 给出开局的建议\n\n"
        f"【用户画像】\n"
        f"玩家等级：{profile.level}\n"
        f"偏好题材：{', '.join(profile.preferred_genres) if profile.preferred_genres else '未设置'}\n"
        f"偏好难度：{profile.preferred_difficulty}\n"
        f"偏好时长：{profile.preferred_duration}\n"
        f"系统标签：{', '.join(profile.tags) if profile.tags else '暂无'}\n"
        f"总游戏局数：{profile.total_games}\n"
        f"总游戏时长：{profile.total_hours}小时\n\n"
        f"【可用剧本库】\n{scripts_str}\n\n"
        "请根据以上信息，友好、简洁地回答用户问题。推荐剧本时请说明推荐理由。"
    )

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

    # 保存对话记录
    db_session = get_session()
    try:
        profile_db = db_session.query(UserProfile).filter(UserProfile.id == user_id).first()
        if profile_db:
            history = profile_db.assistant_chat_history or []
            history.append({"role": "user", "content": req.message})
            history.append({"role": "assistant", "content": reply})
            profile_db.assistant_chat_history = history[-20:]  # 保留最近20条
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
