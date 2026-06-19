"""
EvoMap Murder Game - SQLAlchemy Database Models

剧本、角色、线索、游戏会话、Agent 节点等数据模型。
从 ai-murder-mystery 的 models.py 复用基础结构，新增 Agent 和 Session 相关模型。
"""

import json
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
    version = Column(String, default="1.0.0")
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
    cover_image = Column(Text, default="")        # 封面 URL 或路径
    cover_source = Column(String, default="ai")   # ai / uploaded / none
    cover_image_filename = Column(String, default="")  # 封面文件名（用于文件存储）

    # 凶手设置
    fixed_killer = Column(String, default="")     # 空表示不固定凶手
    hidden_killer = Column(String, default="")    # 隐藏的凶手设定
    player_name = Column(String, default="调查者")
    player_role = Column(String, default="")
    partner_role = Column(String, default="")
    killer_role = Column(String, default="")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    characters = relationship("Character", back_populates="script", cascade="all, delete-orphan")
    quiz_questions = relationship("QuizQuestion", back_populates="script", cascade="all, delete-orphan")
    spoiler_stories = relationship("SpoilerStory", back_populates="script", cascade="all, delete-orphan")
    script_evidences = relationship("ScriptEvidence", back_populates="script", cascade="all, delete-orphan")


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
    is_detective = Column(Boolean, default=False)
    is_killer = Column(Boolean, default=False)
    is_assistant = Column(Boolean, default=False)
    is_player = Column(Boolean, default=False)
    is_partner = Column(Boolean, default=False)
    role_type = Column(String, default="suspect")  # suspect / witness / victim / killer / assistant

    # 头像
    image = Column(Text, default="")
    image_filename = Column(String, default="officer.png")
    image_path = Column(String, default="")
    background_image = Column(Text, default="")

    script = relationship("Script", back_populates="characters")


# ============================
# 剧本级：推理题 / 剧透故事 / 证物定义
# ============================

class QuizQuestion(Base):
    """推理题模型——剧本中的选择题。"""
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    script_id = Column(String, ForeignKey("scripts.id"), nullable=False)
    question = Column(Text, nullable=False)
    choices = Column(Text, default="[]")          # JSON 字符串
    correct_answer = Column(String, default="")
    order_index = Column(Integer, default=0)

    script = relationship("Script", back_populates="quiz_questions")


class SpoilerStory(Base):
    """剧透故事模型——剧本的完整真相还原。"""
    __tablename__ = "spoiler_stories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    script_id = Column(String, ForeignKey("scripts.id"), nullable=False)

    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    word_count = Column(Integer, default=0)
    generation_duration = Column(Float, default=0.0)

    ai_model = Column(String, default="")
    prompt_version = Column(String, default="")
    session_id = Column(String, default="")

    script = relationship("Script", back_populates="spoiler_stories")


class ScriptEvidence(Base):
    """剧本级证物定义——剧本创建时预设的证物模板。"""
    __tablename__ = "script_evidences"

    id = Column(String, primary_key=True)
    script_id = Column(String, ForeignKey("scripts.id"), nullable=False)

    name = Column(String, nullable=False)
    description = Column(Text, default="")
    category = Column(String, default="physical")  # physical / document / digital / testimony / combination
    importance = Column(String, default="medium")   # low / medium / high / critical
    initial_state = Column(String, default="surface")  # hidden / surface / investigated
    image_filename = Column(String, default="")

    related_characters = Column(Text, default="[]")   # JSON array of character names

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    script = relationship("Script", back_populates="script_evidences")


# ============================
# Agent 节点
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
    session_id = Column(String, unique=True)        # EvoMap session_id
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
# 运行时：证物系统
# ============================

class EvidenceRecord(Base):
    """运行时证物——游戏会话中的证物实例，包含动态状态。"""
    __tablename__ = "evidences"

    id = Column(String, primary_key=True)
    script_id = Column(String, ForeignKey("scripts.id"), nullable=False)
    session_id = Column(String, nullable=False)

    name = Column(String, nullable=False)
    basic_description = Column(Text, nullable=False)
    detailed_description = Column(Text, default="")
    deep_description = Column(Text, default="")
    image_path = Column(String, default="")
    category = Column(String, nullable=False)  # physical / document / digital / testimony / combination

    discovery_state = Column(String, nullable=False, default="surface")  # hidden / surface / investigated / analyzed
    unlock_level = Column(Integer, nullable=False, default=1)

    related_actors = Column(JSON, default=list)
    related_evidences = Column(JSON, default=list)
    trigger_events = Column(JSON, default=list)
    combinable_with = Column(JSON, default=list)

    importance = Column(String, nullable=False, default="medium")
    discovered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    is_new = Column(Boolean, default=True)
    has_update = Column(Boolean, default=False)

    reactions = relationship("EvidenceReactionRecord", back_populates="evidence", cascade="all, delete-orphan")
    discoveries = relationship("EvidenceDiscoveryRecord", back_populates="evidence", cascade="all, delete-orphan")
    presentations = relationship("EvidencePresentationRecord", back_populates="evidence", cascade="all, delete-orphan")


class EvidenceReactionRecord(Base):
    """证物反应——角色对特定证物的预设反应。"""
    __tablename__ = "evidence_reactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(String, ForeignKey("evidences.id"), nullable=False)
    actor_name = Column(String, nullable=False)
    actor_id = Column(Integer, nullable=False)
    reaction_type = Column(String, nullable=False)  # basic / contradiction / breakthrough

    basic_response = Column(Text, nullable=False)
    contradiction_trigger = Column(JSON, default=dict)
    breakthrough = Column(JSON, default=dict)

    is_decoy = Column(Boolean, default=False)
    requires_permission = Column(Boolean, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    evidence = relationship("EvidenceRecord", back_populates="reactions")


class EvidenceDiscoveryRecord(Base):
    """证物发现记录——谁在什么情境下发现了证物。"""
    __tablename__ = "evidence_discoveries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(String, ForeignKey("evidences.id"), nullable=False)
    session_id = Column(String, nullable=False)
    actor_name = Column(String, nullable=False)
    discovery_method = Column(String, nullable=False)  # conversation / investigation / combination / deduction
    previous_state = Column(String, nullable=False)
    new_state = Column(String, nullable=False)
    trigger_context = Column(JSON, default=dict)

    discovered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    evidence = relationship("EvidenceRecord", back_populates="discoveries")


class EvidencePresentationRecord(Base):
    """证物出示记录——向角色出示证物及 AI 反应。"""
    __tablename__ = "evidence_presentations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(String, ForeignKey("evidences.id"), nullable=False)
    session_id = Column(String, nullable=False)
    presented_to = Column(String, nullable=False)
    presented_by = Column(String, nullable=False)
    text_content = Column(Text, default="")
    reaction_type = Column(String, nullable=False)
    ai_response = Column(Text, nullable=False)
    new_evidences_unlocked = Column(JSON, default=list)
    information_updated = Column(JSON, default=list)
    presentation_context = Column(Text, default="")

    presented_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    evidence = relationship("EvidenceRecord", back_populates="presentations")


class EvidenceCombinationRecord(Base):
    """证物组合记录——两个证物的组合尝试和结果。"""
    __tablename__ = "evidence_combinations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False)
    primary_evidence_id = Column(String, ForeignKey("evidences.id"), nullable=False)
    secondary_evidence_id = Column(String, ForeignKey("evidences.id"), nullable=False)
    result_evidence_id = Column(String, ForeignKey("evidences.id"), nullable=True)
    combination_success = Column(Boolean, nullable=False)
    combination_result = Column(Text, nullable=False)
    attempted_by = Column(String, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class GameProgressRecord(Base):
    """游戏进度追踪——每个游戏会话的进度状态快照。"""
    __tablename__ = "game_progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False, unique=True)
    script_id = Column(String, ForeignKey("scripts.id"), nullable=False)

    discovered_evidences = Column(JSON, default=list)
    presented_evidences = Column(JSON, default=dict)
    combined_evidences = Column(JSON, default=list)
    investigated_evidences = Column(JSON, default=list)
    contradictions_found = Column(Integer, default=0)
    time_spent = Column(Integer, default=0)
    current_phase = Column(String, default="initial")
    hints_used = Column(Integer, default=0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
    last_activity = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# ============================
# 数据转换工具
# ============================

def script_to_dict(script: Script) -> dict:
    """将数据库 Script 对象转换为前端字典格式。"""
    characters_data = []
    for ch in script.characters:
        characters_data.append({
            "id": ch.id,
            "name": ch.name,
            "bio": ch.bio or "",
            "personality": ch.personality or "",
            "context": ch.context or "",
            "secret": ch.secret or "",
            "violation": ch.violation or "",
            "image": ch.image_filename or ch.image or "officer.png",
            "imagePath": ch.image_path or "",
            "backgroundImage": ch.background_image or "",
            "isVictim": ch.is_victim,
            "isDetective": ch.is_detective,
            "isKiller": ch.is_killer,
            "isAssistant": ch.is_assistant,
            "isPlayer": ch.is_player,
            "isPartner": ch.is_partner,
            "roleType": ch.role_type,
        })

    quiz_data = []
    for q in script.quiz_questions:
        choices = json.loads(q.choices) if isinstance(q.choices, str) else (q.choices or [])
        quiz_data.append({
            "question": q.question,
            "choices": choices,
            "correctAnswer": q.correct_answer,
            "orderIndex": q.order_index,
        })

    evidences_data = []
    for e in script.script_evidences:
        related = json.loads(e.related_characters) if isinstance(e.related_characters, str) else (e.related_characters or [])
        evidences_data.append({
            "id": e.id,
            "name": e.name,
            "description": e.description,
            "category": e.category,
            "importance": e.importance,
            "relatedCharacters": related,
            "initialState": e.initial_state,
            "image": e.image_filename,
        })

    cover = script.cover_image
    if not cover and script.cover_image_filename:
        cover = f"/script_covers/{script.cover_image_filename}"

    return {
        "id": script.id,
        "title": script.title,
        "description": script.description or "",
        "author": script.author or "",
        "version": script.version or "1.0.0",
        "globalStory": script.global_story or "",
        "sourceType": script.source_type,
        "coverImage": cover,
        "coverImageFilename": script.cover_image_filename or "",
        "theme": script.theme,
        "difficulty": script.difficulty,
        "duration": script.duration,
        "emotionLevel": script.emotion_level,
        "inferenceLevel": script.inference_level,
        "horrorLevel": script.horror_level,
        "playerCount": script.player_count,
        "fixedKiller": script.fixed_killer or "",
        "characters": characters_data,
        "evidences": evidences_data,
        "quiz": quiz_data,
        "settings": {
            "theme": script.theme,
            "difficulty": script.difficulty,
            "duration": script.duration,
            "emotionLevel": script.emotion_level,
            "inferenceLevel": script.inference_level,
            "horrorLevel": script.horror_level,
            "playerCount": script.player_count,
            "fixedKiller": script.fixed_killer or "",
            "hiddenKiller": script.hidden_killer or "",
            "playerName": script.player_name,
            "playerRole": script.player_role or "",
            "partnerRole": script.partner_role or "",
            "killerRole": script.killer_role or "",
        },
        "createdAt": script.created_at.isoformat() if script.created_at else "",
        "updatedAt": script.updated_at.isoformat() if script.updated_at else "",
    }


def dict_to_script(data: dict, script: Optional["Script"] = None) -> "Script":
    """将前端字典格式转换为数据库 Script 对象。"""
    if script is None:
        script = Script()

    script.id = data.get("id", script.id)
    script.title = data.get("title", script.title)
    script.description = data.get("description", script.description)
    script.author = data.get("author", script.author)
    script.version = data.get("version", script.version or "1.0.0")
    script.global_story = data.get("globalStory", script.global_story)
    script.source_type = data.get("sourceType", script.source_type)

    script.theme = data.get("theme", script.theme)
    script.difficulty = data.get("difficulty", script.difficulty)
    script.duration = data.get("duration", script.duration)
    script.emotion_level = data.get("emotionLevel", script.emotion_level)
    script.inference_level = data.get("inferenceLevel", script.inference_level)
    script.horror_level = data.get("horrorLevel", script.horror_level)
    script.player_count = data.get("playerCount", script.player_count)
    script.fixed_killer = data.get("fixedKiller", script.fixed_killer)

    # 封面
    cover = data.get("coverImage", "")
    if cover and cover.startswith("/script_covers/"):
        script.cover_image = cover
        script.cover_image_filename = cover.replace("/script_covers/", "")
    elif cover:
        script.cover_image = cover

    # settings 嵌套字段（前端剧本编辑器会发 settings 对象）
    settings = data.get("settings", {})
    if settings:
        script.hidden_killer = settings.get("hiddenKiller", script.hidden_killer)
        script.player_name = settings.get("playerName", script.player_name)
        script.player_role = settings.get("playerRole", script.player_role)
        script.partner_role = settings.get("partnerRole", script.partner_role)
        script.killer_role = settings.get("killerRole", script.killer_role)
        if settings.get("theme"):
            script.theme = settings["theme"]
        if settings.get("difficulty"):
            script.difficulty = settings["difficulty"]
        if settings.get("duration"):
            script.duration = settings["duration"]

    # 处理时间
    if "createdAt" in data and data["createdAt"]:
        try:
            script.created_at = datetime.fromisoformat(data["createdAt"].replace("Z", "+00:00"))
        except (ValueError, TypeError):
            pass

    return script


def dict_to_character(data: dict, script_id: str, character: Optional["Character"] = None) -> "Character":
    """将前端字典格式转换为数据库 Character 对象。"""
    if character is None:
        character = Character()

    character.script_id = script_id
    character.id = data.get("id", character.id)
    character.name = data.get("name", character.name)
    character.bio = data.get("bio", character.bio)
    character.personality = data.get("personality", character.personality)
    character.context = data.get("context", character.context)
    character.secret = data.get("secret", character.secret)
    character.violation = data.get("violation", character.violation)

    image = data.get("image", "officer.png")
    if image.startswith("/character_avatars/"):
        character.image_filename = image.replace("/character_avatars/", "")
        character.image_path = image
    else:
        character.image_filename = image
        character.image_path = f"/character_avatars/{image}"
    character.image = image
    character.background_image = data.get("backgroundImage", character.background_image)

    character.is_victim = data.get("isVictim", character.is_victim)
    character.is_detective = data.get("isDetective", character.is_detective)
    character.is_killer = data.get("isKiller", character.is_killer)
    character.is_assistant = data.get("isAssistant", character.is_assistant)
    character.is_player = data.get("isPlayer", character.is_player)
    character.is_partner = data.get("isPartner", character.is_partner)
    character.role_type = data.get("roleType", character.role_type)

    return character


def dict_to_quiz_question(data: dict, script_id: str, order_index: int = 0) -> "QuizQuestion":
    """将前端字典格式转换为数据库 QuizQuestion 对象。"""
    quiz = QuizQuestion()
    quiz.script_id = script_id
    quiz.question = data.get("question", "")
    quiz.choices = json.dumps(data.get("choices", []), ensure_ascii=False)
    quiz.correct_answer = data.get("correctAnswer", "")
    quiz.order_index = order_index
    return quiz


def dict_to_script_evidence(data: dict, script_id: str, evidence: Optional["ScriptEvidence"] = None) -> "ScriptEvidence":
    """将前端字典格式转换为数据库 ScriptEvidence 对象。"""
    if evidence is None:
        evidence = ScriptEvidence()

    evidence.id = data.get("id", evidence.id)
    evidence.script_id = script_id
    evidence.name = data.get("name", evidence.name)
    evidence.description = data.get("description", evidence.description)
    evidence.category = data.get("category", evidence.category)
    evidence.importance = data.get("importance", evidence.importance)
    evidence.initial_state = data.get("initialState", evidence.initial_state)
    evidence.image_filename = data.get("image", evidence.image_filename)

    related = data.get("relatedCharacters", [])
    evidence.related_characters = json.dumps(related, ensure_ascii=False)

    return evidence


def spoiler_story_to_dict(story: "SpoilerStory") -> dict:
    """将数据库 SpoilerStory 对象转换为字典格式。"""
    return {
        "id": story.id,
        "scriptId": story.script_id,
        "title": story.title,
        "content": story.content,
        "generatedAt": story.generated_at.isoformat() if story.generated_at else "",
        "wordCount": story.word_count,
        "generationDuration": story.generation_duration,
        "aiModel": story.ai_model,
        "promptVersion": story.prompt_version,
        "sessionId": story.session_id,
    }


def dict_to_spoiler_story(data: dict, script_id: str) -> "SpoilerStory":
    """将字典格式转换为数据库 SpoilerStory 对象。"""
    story = SpoilerStory()
    story.script_id = script_id
    story.title = data.get("title", "剧透故事")
    story.content = data.get("content", "")
    story.word_count = len(data.get("content", ""))
    story.generation_duration = data.get("generationDuration", 0.0)
    story.ai_model = data.get("aiModel", "")
    story.prompt_version = data.get("promptVersion", "")
    story.session_id = data.get("sessionId", "")

    if "generatedAt" in data and data["generatedAt"]:
        try:
            story.generated_at = datetime.fromisoformat(data["generatedAt"].replace("Z", "+00:00"))
        except (ValueError, TypeError):
            pass

    return story


def evidence_record_to_dict(evidence: "EvidenceRecord") -> dict:
    """将数据库 EvidenceRecord 对象转换为前端字典格式。"""
    reactions_data = []
    for r in evidence.reactions:
        reactions_data.append({
            "actorName": r.actor_name,
            "actorId": r.actor_id,
            "reactionType": r.reaction_type,
            "basicResponse": r.basic_response,
            "contradictionTrigger": r.contradiction_trigger,
            "breakthrough": r.breakthrough,
            "isDecoy": r.is_decoy,
            "requiresPermission": r.requires_permission,
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


def dict_to_evidence_record(data: dict, evidence: Optional["EvidenceRecord"] = None) -> "EvidenceRecord":
    """将字典格式转换为数据库 EvidenceRecord 对象。"""
    if evidence is None:
        evidence = EvidenceRecord()

    evidence.id = data.get("id", evidence.id)
    evidence.script_id = data.get("scriptId", evidence.script_id)
    evidence.session_id = data.get("sessionId", evidence.session_id)
    evidence.name = data.get("name", evidence.name)
    evidence.basic_description = data.get("basicDescription", evidence.basic_description)
    evidence.detailed_description = data.get("detailedDescription", evidence.detailed_description)
    evidence.deep_description = data.get("deepDescription", evidence.deep_description)
    evidence.image_path = data.get("image", evidence.image_path)
    evidence.category = data.get("category", evidence.category)
    evidence.discovery_state = data.get("discoveryState", evidence.discovery_state)
    evidence.unlock_level = data.get("unlockLevel", evidence.unlock_level)
    evidence.related_actors = data.get("relatedActors", evidence.related_actors)
    evidence.related_evidences = data.get("relatedEvidences", evidence.related_evidences)
    evidence.trigger_events = data.get("triggerEvents", evidence.trigger_events)
    evidence.combinable_with = data.get("combinableWith", evidence.combinable_with)
    evidence.importance = data.get("importance", evidence.importance)
    evidence.is_new = data.get("isNew", evidence.is_new)
    evidence.has_update = data.get("hasUpdate", evidence.has_update)

    if "discoveredAt" in data and data["discoveredAt"]:
        try:
            evidence.discovered_at = datetime.fromisoformat(data["discoveredAt"].replace("Z", "+00:00"))
        except (ValueError, TypeError):
            pass

    return evidence


# ============================
# Database Setup
# ============================

def get_engine():
    """获取数据库引擎——PostgreSQL（如果配置）否则 SQLite。"""
    if DB_CONN_URL:
        return create_engine(DB_CONN_URL, echo=False)
    return create_engine(f"sqlite:///{SQLITE_PATH}", echo=False)


def init_db():
    """初始化数据库——创建所有表（幂等，仅新增不覆盖）。"""
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """获取 SQLAlchemy Session。"""
    engine = get_engine()
    return Session(engine)
