"""
EvoMap Murder Game - SQLAlchemy Database Models

剧本、角色、线索、游戏会话、Agent 节点等数据模型。
从 ai-murder-mystery 的 models.py 复用基础结构，新增 Agent 和 Session 相关模型。
"""

from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, JSON,
    DateTime, ForeignKey, create_engine,
)
from sqlalchemy.orm import DeclarativeBase, relationship, Session
from datetime import datetime, timezone
from typing import Optional

from api.config.settings import DB_CONN_URL, SQLITE_PATH


class Base(DeclarativeBase):
    pass


# ============================
# 剧本与角色
# ============================

class Script(Base):
    """剧本模型——定义一个完整的剧本杀剧本。"""
    __tablename__ = "scripts"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    author = Column(String, default="")
    global_story = Column(Text, default="")
    source_type = Column(String, default="manual")  # manual / ai_generated / imported

    # 分类标签
    theme = Column(String, default="modern")    # modern / ancient / horror / campus / ...
    difficulty = Column(String, default="medium")  # easy / medium / hard
    duration = Column(Integer, default=120)      # 预计时长（分钟）
    emotion_level = Column(Float, default=0.5)   # 情感浓度 0-1
    inference_level = Column(Float, default=0.5)  # 推理难度 0-1
    horror_level = Column(Float, default=0.0)    # 恐怖程度 0-1
    player_count = Column(Integer, default=6)

    # 封面
    cover_image = Column(Text, default="")
    cover_source = Column(String, default="ai")  # ai / uploaded / none

    # 凶手设置
    fixed_killer = Column(String, default="")    # 空表示不固定凶手

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    characters = relationship("Character", back_populates="script", cascade="all, delete-orphan")


class Character(Base):
    """角色模型——剧本中的每个角色。"""
    __tablename__ = "characters"

    id = Column(String, primary_key=True)
    script_id = Column(String, ForeignKey("scripts.id"), nullable=False)
    name = Column(String, nullable=False)
    bio = Column(Text, default="")
    personality = Column(Text, default="")
    context = Column(Text, default="")
    secret = Column(Text, default="")
    violation = Column(Text, default="")

    # 角色标记
    is_victim = Column(Boolean, default=False)
    is_killer = Column(Boolean, default=False)
    is_assistant = Column(Boolean, default=False)
    is_player = Column(Boolean, default=False)
    is_partner = Column(Boolean, default=False)
    role_type = Column(String, default="suspect")  # suspect / witness / victim / killer / assistant

    # 头像
    image = Column(Text, default="")
    background_image = Column(Text, default="")

    script = relationship("Script", back_populates="characters")


# ============================
# Agent 节点（新增）
# ============================

class AgentNode(Base):
    """Agent 节点模型——注册到 EvoMap 网络的 Agent 实例。"""
    __tablename__ = "agent_nodes"

    id = Column(String, primary_key=True)          # 内部ID
    node_id = Column(String, unique=True, nullable=False)  # EvoMap node_id
    node_secret = Column(String, nullable=False)   # ⚠️ 不对外暴露
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)           # dm / companion / assistant
    model = Column(String, default="evomap-gemini-3.1-pro-preview")
    domains = Column(JSON, default=[])

    # Agent 的持久化身份
    identity_doc = Column(Text, default="")
    constitution = Column(Text, default="")

    # EvoMap 状态
    status = Column(String, default="alive")
    claim_url = Column(String, default="")
    credit_balance = Column(Integer, default=100)
    reputation = Column(Float, default=50.0)
    level = Column(Integer, default=2)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))


# ============================
# 游戏会话（新增）
# ============================

class GameSession(Base):
    """游戏会话模型——一次完整游戏的记录。"""
    __tablename__ = "game_sessions"

    id = Column(String, primary_key=True)
    session_id = Column(String, unique=True)        # EvoMap session_id
    script_id = Column(String, ForeignKey("scripts.id"))
    topic = Column(String, default="")
    status = Column(String, default="active")        # active / paused / completed / failed

    # 参与者
    dm_node_id = Column(String, default="")
    companion_node_ids = Column(JSON, default=[])
    assistant_node_id = Column(String, default="")
    player_user_id = Column(String, default="")

    # 游戏进度
    current_phase = Column(String, default="intro")  # intro / investigation / voting / reveal / review
    phase_history = Column(JSON, default=[])

    # 游戏结果
    result = Column(JSON, default={})                # 最终结果数据

    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ended_at = Column(DateTime, nullable=True)


# ============================
# 对话记录
# ============================

class ConversationTurn(Base):
    """对话记录模型——每轮对话的原始/批评/修订/最终回复。"""
    __tablename__ = "conversation_turns"

    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False)
    actor_name = Column(String, nullable=False)
    chat_messages = Column(JSON, default=[])

    original_response = Column(Text, default="")
    critique_response = Column(Text, default="")
    refined_response = Column(Text, default="")
    final_response = Column(Text, default="")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ============================
# 进化记忆记录（新增）
# ============================

class EvolutionRecord(Base):
    """Agent 进化记录——每次 Memory record 的本地副本。"""
    __tablename__ = "evolution_records"

    id = Column(String, primary_key=True)
    agent_node_id = Column(String, ForeignKey("agent_nodes.id"))
    session_id = Column(String, default="")
    signals = Column(JSON, default=[])
    gene_id = Column(String, default="")
    status = Column(String, default="success")
    score = Column(Float, default=0.0)
    summary = Column(Text, default="")

    # 进化变更（constitution/identity_doc 更新）
    update_type = Column(String, default="")  # constitution / identity_doc / none
    old_content = Column(Text, default="")
    new_content = Column(Text, default="")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ============================
# Database Setup
# ============================

def get_engine():
    """获取数据库引擎——PostgreSQL（如果配置）否则 SQLite。"""
    if DB_CONN_URL:
        return create_engine(DB_CONN_URL, echo=False)
    return create_engine(f"sqlite:///{SQLITE_PATH}", echo=False)


def init_db():
    """初始化数据库——创建所有表。"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """获取 SQLAlchemy Session。"""
    engine = get_engine()
    return Session(engine)
