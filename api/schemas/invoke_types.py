"""
EvoMap Murder Game - Pydantic Request/Response Types

定义所有 API 端点的请求和响应模型。
"""

from pydantic import BaseModel, Field
from typing import Optional, List


# ============================
# Actor（角色/Agent）模型
# ============================

class SafeActor(BaseModel):
    """安全版本的角色信息——过滤掉 secret/violation 等敏感字段。

    发送给其他 Agent 时，只传递角色公开信息，防止信息泄露。
    这是从 ai-murder-mystery 的 SafeActor 机制复用而来的核心隔离策略。
    """
    id: str
    name: str
    bio: str = ""
    personality: str = ""
    context: str = ""
    image: Optional[str] = None
    is_victim: bool = False
    is_killer: bool = False
    is_assistant: bool = False
    is_player: bool = False
    is_partner: bool = False
    role_type: str = "suspect"


class Actor(BaseModel):
    """完整角色信息——包含 secret/violation 等敏感字段。

    仅在 DM-Agent 和角色自己使用时传递，绝不发给其他 Agent。
    """
    id: str
    name: str
    bio: str = ""
    personality: str = ""
    context: str = ""
    secret: str = ""
    violation: str = ""
    image: Optional[str] = None
    background_image: Optional[str] = None
    is_victim: bool = False
    is_killer: bool = False
    is_assistant: bool = False
    is_player: bool = False
    is_partner: bool = False
    role_type: str = "suspect"


class LLMMessage(BaseModel):
    """对话消息模型。"""
    role: str = "user"
    content: str = ""


# ============================
# API Request/Response
# ============================

class InvocationRequest(BaseModel):
    """AI 调用请求——发送到 /invoke 或 /invoke/stream。"""
    global_story: str = ""
    actor: Actor
    session_id: str = ""
    detective_name: str = "侦探"
    victim_name: str = ""
    all_actors: List[SafeActor] = []
    chat_messages: List[LLMMessage] = []
    temperature: float = 0.7
    speech_phase: str = ""  # intro / discussion — 公共发言阶段专用指引


class InvocationResponse(BaseModel):
    """AI 调用响应。"""
    original: str = ""
    critique: Optional[str] = ""
    refined: Optional[str] = ""
    final_response: str = ""


class AgentRegistrationRequest(BaseModel):
    """Agent 注册请求。"""
    role: str = "companion"  # dm / companion / assistant
    name: str = ""
    model: str = "evomap-gemini-3.1-pro-preview"
    identity_doc: str = ""
    constitution: str = ""


class AgentRegistrationResponse(BaseModel):
    """Agent 注册响应。"""
    node_id: str = ""
    node_secret: str = ""
    claim_url: str = ""
    claim_code: str = ""
    status: str = "alive"
    mode: str = "evomap"  # evomap / local
    warning: str = ""


class GameSessionRequest(BaseModel):
    """创建游戏 Session 请求。"""
    script_id: str = ""
    topic: str = ""
    player_character_name: str = ""  # 玩家选择扮演的角色名，为空则使用 is_player 角色


class GameSessionResponse(BaseModel):
    """创建游戏 Session 响应。"""
    session_id: str = ""
    participants: List[str] = []
    status: str = "active"


class MemoryRecordRequest(BaseModel):
    """记录经验请求。"""
    node_id: str = ""
    signals: List[str] = []
    gene_id: str = ""
    status: str = "success"
    score: float = 0.0
    summary: str = ""


class MemoryRecallRequest(BaseModel):
    """召回经验请求。"""
    node_id: str = ""
    signals: List[str] = []
    limit: int = 5


class EvolutionUpdateRequest(BaseModel):
    """Agent 进化更新请求——改写 constitution 或 identity_doc。"""
    node_id: str = ""
    update_type: str = "constitution"  # constitution / identity_doc
    new_content: str = ""
