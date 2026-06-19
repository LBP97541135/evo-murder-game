"""
EvoMap Murder Game - SQLAlchemy Database Models

剧本、角色、证据、游戏会话、Agent 节点、对话记录、进化记录等数据模型。
从 ai-murder-mystery 复用核心游戏流程的数据模型，新增 Agent 和 Session 相关模型。
"""

from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, JSON,
    DateTime, ForeignKey, create_engine,
)
from sqlalchemy.orm import DeclarativeBase, relationship, Session as DBSession
from datetime import datetime, timezone

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
    theme = Column(String, default="modern")
    difficulty = Column(String, default="medium")
    duration = Column(Integer, default=120)
    emotion_level = Column(Float, default=0.5)
    inference_level = Column(Float, default=0.5)
    horror_level = Column(Float, default=0.0)
    player_count = Column(Integer, default=6)

    # 封面
    cover_image = Column(Text, default="")
    cover_image_filename = Column(String, default="")
    cover_image_path = Column(String, default="")
    cover_source = Column(String, default="ai")

    # 凶手设置
    fixed_killer = Column(String, default="")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    characters = relationship("Character", back_populates="script", cascade="all, delete-orphan")
    evidences = relationship("ScriptEvidence", back_populates="script", cascade="all, delete-orphan")
    quiz_questions = relationship("QuizQuestion", back_populates="script", cascade="all, delete-orphan")


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
    role_type = Column(String, default="suspect")

    # 头像
    image = Column(Text, default="")
    image_filename = Column(String, default="")
    image_path = Column(String, default="")
    background_image = Column(Text, default="")

    script = relationship("Script", back_populates="characters")


class QuizQuestion(Base):
    """题目模型——推理验证用的选择题。"""
    __tablename__ = "quiz_questions"

    id = Column(String, primary_key=True)
    script_id = Column(String, ForeignKey("scripts.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSON, default=[])
    correct_answer = Column(String, default="")
    order_index = Column(Integer, default=0)

    script = relationship("Script", back_populates="quiz_questions")


class ScriptEvidence(Base):
    """剧本证物定义——剧本中的静态证物配置，游戏开始时初始化为 EvidenceRecord。"""
    __tablename__ = "script_evidences"

    id = Column(String, primary_key=True)
    script_id = Column(String, ForeignKey("scripts.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    category = Column(String, default="physical")  # physical / document / digital / testimony / combination
    importance = Column(String, default="medium")  # low / medium / high / critical
    related_characters = Column(JSON, default=[])
    initial_state = Column(JSON, default={})
    image_filename = Column(String, default="")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    script = relationship("Script", back_populates="evidences")


class SpoilerStory(Base):
    """剧透故事——AI生成的完整真相叙事。"""
    __tablename__ = "spoiler_stories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    script_id = Column(String, ForeignKey("scripts.id"), nullable=False)
    title = Column(String, default="")
    content = Column(Text, default="")
    word_count = Column(Integer, default=0)
    ai_model = Column(String, default="")
    prompt_version = Column(String, default="")
    generation_duration = Column(Float, default=0.0)

    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ============================
# 证据（游戏运行时）
# ============================

class EvidenceRecord(Base):
    """游戏运行时证物——从 ScriptEvidence 初始化，游戏过程中动态变化。"""
    __tablename__ = "evidences"

    id = Column(String, primary_key=True)
    script_id = Column(String, ForeignKey("scripts.id"), nullable=False)
    session_id = Column(String, nullable=False)

    # 基础信息
    name = Column(String, nullable=False)
    basic_description = Column(Text, nullable=False)
    detailed_description = Column(Text)   # 搭档分析信息（解锁等级>=2时AI可见）
    deep_description = Column(Text)       # 深度调查信息（解锁等级>=3时AI可见）
    image_path = Column(String)
    category = Column(String, nullable=False, default="physical")

    # 状态管理
    discovery_state = Column(String, nullable=False, default="surface")  # hidden / surface / investigated / analyzed
    unlock_level = Column(Integer, nullable=False, default=1)  # 1-3

    # 关联系统
    related_actors = Column(JSON, default=[])
    related_evidences = Column(JSON, default=[])
    trigger_events = Column(JSON, default=[])
    combinable_with = Column(JSON, default=[])

    # 元数据
    importance = Column(String, nullable=False, default="medium")
    discovered_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # 显示状态
    is_new = Column(Boolean, default=True)
    has_update = Column(Boolean, default=False)

    # 关联关系
    reactions = relationship("EvidenceReactionRecord", back_populates="evidence", cascade="all, delete-orphan")
    discoveries = relationship("EvidenceDiscoveryRecord", back_populates="evidence", cascade="all, delete-orphan")
    presentations = relationship("EvidencePresentationRecord", back_populates="evidence", cascade="all, delete-orphan")


class EvidenceReactionRecord(Base):
    """角色对证物的反应配置。"""
    __tablename__ = "evidence_reactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(String, ForeignKey("evidences.id"), nullable=False)
    actor_name = Column(String, nullable=False)
    actor_id = Column(Integer, nullable=False)
    reaction_type = Column(String, nullable=False)  # basic / contradiction / breakthrough

    basic_response = Column(Text, nullable=False)
    contradiction_trigger = Column(JSON)
    breakthrough = Column(JSON)

    is_decoy = Column(Boolean, default=False)
    requires_permission = Column(Boolean, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    evidence = relationship("EvidenceRecord", back_populates="reactions")


class EvidenceDiscoveryRecord(Base):
    """证物发现历史记录。"""
    __tablename__ = "evidence_discoveries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(String, ForeignKey("evidences.id"), nullable=False)
    session_id = Column(String, nullable=False)
    actor_name = Column(String, nullable=False)
    discovery_method = Column(String, nullable=False)  # conversation / investigation / combination / deduction
    previous_state = Column(String, nullable=False)
    new_state = Column(String, nullable=False)
    trigger_context = Column(JSON)

    discovered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    evidence = relationship("EvidenceRecord", back_populates="discoveries")


class EvidencePresentationRecord(Base):
    """证物出示记录——向角色出示证物时的完整记录。"""
    __tablename__ = "evidence_presentations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(String, ForeignKey("evidences.id"), nullable=False)
    session_id = Column(String, nullable=False)
    presented_to = Column(String, nullable=False)
    presented_by = Column(String, nullable=False)
    text_content = Column(Text)
    reaction_type = Column(String, nullable=False)  # basic / contradiction / breakthrough
    ai_response = Column(Text, nullable=False)
    new_evidences_unlocked = Column(JSON, default=[])
    information_updated = Column(JSON, default=[])
    presentation_context = Column(Text)

    presented_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    evidence = relationship("EvidenceRecord", back_populates="presentations")


class EvidenceCombinationRecord(Base):
    """证物组合记录——两个证物组合产生新证物。"""
    __tablename__ = "evidence_combinations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False)
    primary_evidence_id = Column(String, ForeignKey("evidences.id"), nullable=False)
    secondary_evidence_id = Column(String, ForeignKey("evidences.id"), nullable=False)
    result_evidence_id = Column(String, ForeignKey("evidences.id"))
    combination_success = Column(Boolean, nullable=False)
    combination_result = Column(Text, nullable=False)
    attempted_by = Column(String, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class GameProgressRecord(Base):
    """游戏进度记录——跟踪证物发现、出示、组合等进度。"""
    __tablename__ = "game_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False, unique=True)
    script_id = Column(String, ForeignKey("scripts.id"), nullable=False)

    discovered_evidences = Column(JSON, default=[])
    presented_evidences = Column(JSON, default={})
    combined_evidences = Column(JSON, default=[])
    investigated_evidences = Column(JSON, default=[])
    contradictions_found = Column(Integer, default=0)
    time_spent = Column(Integer, default=0)
    current_phase = Column(String, default="initial")  # initial / investigation / confrontation / resolution
    hints_used = Column(Integer, default=0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
    last_activity = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ============================
# Agent 节点
# ============================

class AgentNode(Base):
    """Agent 节点模型——注册到 EvoMap 网络的 Agent 实例。"""
    __tablename__ = "agent_nodes"

    id = Column(String, primary_key=True)
    node_id = Column(String, unique=True, nullable=False)
    node_secret = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    model = Column(String, default="evomap-gemini-3.1-pro-preview")
    domains = Column(JSON, default=[])

    identity_doc = Column(Text, default="")
    constitution = Column(Text, default="")

    status = Column(String, default="alive")
    claim_url = Column(String, default="")
    credit_balance = Column(Integer, default=100)
    reputation = Column(Float, default=50.0)
    level = Column(Integer, default=2)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))


# ============================
# 游戏会话
# ============================

class GameSession(Base):
    """游戏会话模型——一次完整游戏的记录。"""
    __tablename__ = "game_sessions"

    id = Column(String, primary_key=True)
    session_id = Column(String, unique=True)
    script_id = Column(String, ForeignKey("scripts.id"))
    topic = Column(String, default="")
    status = Column(String, default="active")

    dm_node_id = Column(String, default="")
    companion_node_ids = Column(JSON, default=[])
    assistant_node_id = Column(String, default="")
    player_user_id = Column(String, default="")

    current_phase = Column(String, default="intro")
    phase_history = Column(JSON, default=[])
    result = Column(JSON, default={})

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
# 进化记忆记录
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

    update_type = Column(String, default="")
    old_content = Column(Text, default="")
    new_content = Column(Text, default="")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ============================
# 数据转换工具函数
# ============================

def script_to_dict(script: Script) -> dict:
    """将 Script 对象转为前端需要的字典。"""
    return {
        "id": script.id,
        "title": script.title,
        "description": script.description,
        "author": script.author,
        "globalStory": script.global_story,
        "sourceType": script.source_type,
        "theme": script.theme,
        "difficulty": script.difficulty,
        "duration": script.duration,
        "emotionLevel": script.emotion_level,
        "inferenceLevel": script.inference_level,
        "horrorLevel": script.horror_level,
        "playerCount": script.player_count,
        "coverImage": script.cover_image,
        "coverImageFilename": script.cover_image_filename,
        "coverImagePath": script.cover_image_path,
        "fixedKiller": script.fixed_killer,
        "characters": [character_to_dict(c) for c in script.characters],
        "evidences": [script_evidence_to_dict(e) for e in script.evidences],
        "quiz": [quiz_question_to_dict(q) for q in script.quiz_questions],
        "createdAt": script.created_at.isoformat() if script.created_at else None,
        "updatedAt": script.updated_at.isoformat() if script.updated_at else None,
    }


def dict_to_script(data: dict, script: Script = None) -> Script:
    """将前端字典转为 Script 对象。"""
    if script is None:
        script = Script()
    script.id = data.get("id")
    script.title = data.get("title", "")
    script.description = data.get("description", "")
    script.author = data.get("author", "")
    script.global_story = data.get("globalStory", "")
    script.source_type = data.get("sourceType", "manual")
    script.theme = data.get("theme", "modern")
    script.difficulty = data.get("difficulty", "medium")
    script.duration = data.get("duration", 120)
    script.emotion_level = data.get("emotionLevel", 0.5)
    script.inference_level = data.get("inferenceLevel", 0.5)
    script.horror_level = data.get("horrorLevel", 0.0)
    script.player_count = data.get("playerCount", 6)
    script.cover_image = data.get("coverImage", "")
    script.fixed_killer = data.get("fixedKiller", "")
    return script


def character_to_dict(character: Character) -> dict:
    """将 Character 对象转为前端字典。"""
    return {
        "id": character.id,
        "name": character.name,
        "bio": character.bio,
        "personality": character.personality,
        "context": character.context,
        "secret": character.secret,
        "violation": character.violation,
        "isVictim": character.is_victim,
        "isKiller": character.is_killer,
        "isAssistant": character.is_assistant,
        "isPlayer": character.is_player,
        "isPartner": character.is_partner,
        "roleType": character.role_type,
        "image": character.image or character.image_path or "",
        "backgroundImage": character.background_image,
    }


def dict_to_character(data: dict, script_id: str, character: Character = None) -> Character:
    """将前端字典转为 Character 对象。"""
    if character is None:
        character = Character()
    character.id = data.get("id")
    character.script_id = script_id
    character.name = data.get("name", "")
    character.bio = data.get("bio", "")
    character.personality = data.get("personality", "")
    character.context = data.get("context", "")
    character.secret = data.get("secret", "")
    character.violation = data.get("violation", "")
    character.is_victim = data.get("isVictim", False)
    character.is_killer = data.get("isKiller", False)
    character.is_assistant = data.get("isAssistant", False)
    character.is_player = data.get("isPlayer", False)
    character.is_partner = data.get("isPartner", False)
    character.role_type = data.get("roleType", "suspect")
    character.image = data.get("image", "")
    character.background_image = data.get("backgroundImage", "")
    return character


def script_evidence_to_dict(evidence: ScriptEvidence) -> dict:
    """将 ScriptEvidence 对象转为前端字典。"""
    return {
        "id": evidence.id,
        "name": evidence.name,
        "description": evidence.description,
        "category": evidence.category,
        "importance": evidence.importance,
        "relatedCharacters": evidence.related_characters or [],
        "initialState": evidence.initial_state or {},
        "image": evidence.image_filename,
    }


def dict_to_script_evidence(data: dict, script_id: str, evidence: ScriptEvidence = None) -> ScriptEvidence:
    """将前端字典转为 ScriptEvidence 对象。"""
    if evidence is None:
        evidence = ScriptEvidence()
    evidence.id = data.get("id")
    evidence.script_id = script_id
    evidence.name = data.get("name", "")
    evidence.description = data.get("description", "")
    evidence.category = data.get("category", "physical")
    evidence.importance = data.get("importance", "medium")
    evidence.related_characters = data.get("relatedCharacters", [])
    evidence.initial_state = data.get("initialState", {})
    evidence.image_filename = data.get("image", "")
    return evidence


def quiz_question_to_dict(question: QuizQuestion) -> dict:
    """将 QuizQuestion 对象转为前端字典。"""
    return {
        "id": question.id,
        "question": question.question_text,
        "options": question.options or [],
        "correctAnswer": question.correct_answer,
    }


def dict_to_quiz_question(data: dict, script_id: str, order_index: int = 0,
                          question: QuizQuestion = None) -> QuizQuestion:
    """将前端字典转为 QuizQuestion 对象。"""
    if question is None:
        question = QuizQuestion()
    question.id = data.get("id")
    question.script_id = script_id
    question.question_text = data.get("question", "")
    question.options = data.get("options", [])
    question.correct_answer = data.get("correctAnswer", "")
    question.order_index = order_index
    return question


def evidence_record_to_dict(evidence: EvidenceRecord) -> dict:
    """将游戏运行时 EvidenceRecord 转为前端字典（camelCase）。"""
    reactions_data = []
    for reaction in evidence.reactions:
        reactions_data.append({
            "actorName": reaction.actor_name,
            "actorId": reaction.actor_id,
            "reactionType": reaction.reaction_type,
            "basicResponse": reaction.basic_response,
            "contradictionTrigger": reaction.contradiction_trigger,
            "breakthrough": reaction.breakthrough,
            "isDecoy": reaction.is_decoy,
            "requiresPermission": reaction.requires_permission,
        })
    return {
        "id": evidence.id,
        "name": evidence.name,
        "basicDescription": evidence.basic_description,
        "detailedDescription": evidence.detailed_description,
        "deepDescription": evidence.deep_description,
        "image": evidence.image_path,
        "category": evidence.category,
        "discoveryState": evidence.discovery_state,
        "unlockLevel": evidence.unlock_level,
        "relatedActors": evidence.related_actors or [],
        "relatedEvidences": evidence.related_evidences or [],
        "triggerEvents": evidence.trigger_events or [],
        "reactions": reactions_data,
        "combinableWith": evidence.combinable_with or [],
        "importance": evidence.importance,
        "sessionId": evidence.session_id,
        "scriptId": evidence.script_id,
        "discoveredAt": evidence.discovered_at.isoformat() if evidence.discovered_at else None,
        "lastUpdated": evidence.updated_at.isoformat() if evidence.updated_at else None,
        "isNew": evidence.is_new,
        "hasUpdate": evidence.has_update,
    }


def presentation_record_to_dict(presentation: EvidencePresentationRecord) -> dict:
    """将 EvidencePresentationRecord 转为前端字典。"""
    return {
        "id": str(presentation.id),
        "evidenceId": presentation.evidence_id,
        "sessionId": presentation.session_id,
        "presentedTo": presentation.presented_to,
        "presentedBy": presentation.presented_by,
        "textContent": presentation.text_content,
        "reactionType": presentation.reaction_type,
        "aiResponse": presentation.ai_response,
        "newEvidencesUnlocked": presentation.new_evidences_unlocked or [],
        "informationUpdated": presentation.information_updated or [],
        "presentationContext": presentation.presentation_context,
        "presentedAt": presentation.presented_at.isoformat() if presentation.presented_at else None,
    }


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


def get_db():
    """获取 SQLAlchemy Session（用于 Depends 注入）。"""
    engine = get_engine()
    db = DBSession(engine)
    try:
        yield db
    finally:
        db.close()
