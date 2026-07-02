# -*- coding: utf-8 -*-
"""核心流程 Smoke Tests

覆盖游戏核心流程的服务层测试，使用 Mock 数据库验证各服务和路由的基本行为。
"""
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime


# ---------------------------------------------------------------------------
# 1. 健康检查
# ---------------------------------------------------------------------------
def test_health_endpoint():
    """GET /health 返回 200 和统一格式"""
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "ok"


# ---------------------------------------------------------------------------
# 2. 创建游戏会话
# ---------------------------------------------------------------------------
def test_create_session_service():
    """SessionService.create_session 创建会话并返回对象"""
    from api.services.session_service import SessionService

    db = Mock()
    service = SessionService(db)
    service.repo = Mock()

    mock_session = Mock()
    mock_session.id = "session_001"
    mock_session.script_id = "script_001"
    mock_session.status = "active"
    mock_session.current_phase = "setup"
    service.repo.create = Mock(return_value=mock_session)

    result = service.create_session({"script_id": "script_001", "title": "测试会话"})
    assert result is not None
    assert result.script_id == "script_001"
    service.repo.create.assert_called_once()


# ---------------------------------------------------------------------------
# 3. 获取剧本列表
# ---------------------------------------------------------------------------
def test_get_scripts_repository():
    """ScriptRepository.get_all 返回剧本列表"""
    from api.repositories.script_repository import ScriptRepository

    db = Mock()
    repo = ScriptRepository(db)

    mock_query = Mock()
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [Mock(id="s1"), Mock(id="s2")]
    db.query.return_value = mock_query

    scripts = repo.get_all(status="active")
    assert len(scripts) == 2


# ---------------------------------------------------------------------------
# 4. 选角流程
# ---------------------------------------------------------------------------
def test_casting_service_cast_session():
    """CastingService.cast_session 批量分配角色"""
    from api.services.casting_service import CastingService

    db = Mock()
    service = CastingService(db)
    service.repo = Mock()

    mock_cast = Mock()
    mock_cast.id = "cast_001"
    mock_cast.session_id = "session_001"
    mock_cast.character_id = "char_001"
    service.repo.create_cast = Mock(return_value=mock_cast)

    casts_data = [
        {"character_id": "char_001", "actor_type": "human", "actor_id": "user_1"},
    ]
    result = service.cast_session("session_001", casts_data)
    assert len(result) == 1
    assert result[0].character_id == "char_001"


def test_casting_service_get_casts():
    """CastingService.get_casts 获取角色分配列表"""
    from api.services.casting_service import CastingService

    db = Mock()
    service = CastingService(db)
    service.repo = Mock()
    service.repo.get_casts = Mock(return_value=[Mock(id="cast_001")])

    result = service.get_casts("session_001")
    assert len(result) == 1


def test_casting_service_reset_casts():
    """CastingService.reset_casts 重置角色分配"""
    from api.services.casting_service import CastingService

    db = Mock()
    service = CastingService(db)
    service.repo = Mock()
    service.repo.delete_casts_by_session = Mock(return_value=True)

    result = service.reset_casts("session_001")
    assert result is True


# ---------------------------------------------------------------------------
# 5. 阶段推进
# ---------------------------------------------------------------------------
def test_phase_service_advance():
    """PhaseService.advance_phase 推进到下一阶段"""
    from api.services.phase_service import PhaseService

    db = Mock()
    service = PhaseService(db)
    service.repo = Mock()

    mock_session = Mock()
    mock_session.id = "session_001"
    mock_session.current_phase = "setup"
    service.repo.get_by_id = Mock(return_value=mock_session)
    service.repo.update = Mock(return_value=mock_session)
    service.repo.create_phase_event = Mock()

    result = service.advance_phase("session_001")
    assert result["from_phase"] == "setup"
    assert result["to_phase"] == "intro"
    assert "event_id" in result


def test_phase_service_get_current_phase():
    """PhaseService.get_current_phase 返回当前阶段"""
    from api.services.phase_service import PhaseService

    db = Mock()
    service = PhaseService(db)
    service.repo = Mock()

    mock_session = Mock()
    mock_session.current_phase = "investigation"
    service.repo.get_by_id = Mock(return_value=mock_session)

    result = service.get_current_phase("session_001")
    assert result == "investigation"


def test_phase_service_advance_at_final_phase_raises():
    """PhaseService.advance_phase 在最终阶段抛出异常"""
    from api.services.phase_service import PhaseService

    db = Mock()
    service = PhaseService(db)
    service.repo = Mock()

    mock_session = Mock()
    mock_session.current_phase = "review"
    service.repo.get_by_id = Mock(return_value=mock_session)

    try:
        service.advance_phase("session_001")
        assert False, "应该抛出 ValueError"
    except ValueError:
        pass


def test_phase_service_force_phase():
    """PhaseService.force_phase 强制跳转阶段"""
    from api.services.phase_service import PhaseService

    db = Mock()
    service = PhaseService(db)
    service.repo = Mock()

    mock_session = Mock()
    mock_session.current_phase = "setup"
    service.repo.get_by_id = Mock(return_value=mock_session)
    service.repo.update = Mock(return_value=mock_session)
    service.repo.create_phase_event = Mock()

    result = service.force_phase("session_001", "voting", "admin_force")
    assert result["to_phase"] == "voting"
    assert result["reason"] == "admin_force"


# ---------------------------------------------------------------------------
# 6. 对话系统
# ---------------------------------------------------------------------------
def test_conversation_create_thread():
    """ConversationService.create_thread 创建对话线程"""
    from api.services.conversation_service import ConversationService

    db = Mock()
    service = ConversationService(db)
    service.repo = Mock()

    mock_thread = Mock()
    mock_thread.id = "thread_001"
    mock_thread.session_id = "session_001"
    mock_thread.thread_type = "public"
    service.repo.create_thread = Mock(return_value=mock_thread)

    result = service.create_thread("session_001", "public", ["user_1"])
    assert result.thread_type == "public"
    assert result.session_id == "session_001"


def test_conversation_send_message():
    """ConversationService.send_message 发送消息"""
    from api.services.conversation_service import ConversationService

    db = Mock()
    service = ConversationService(db)
    service.repo = Mock()

    mock_msg = Mock()
    mock_msg.id = "msg_001"
    mock_msg.content = "你好"
    mock_msg.sender_type = "human"
    service.repo.create_message = Mock(return_value=mock_msg)

    result = service.send_message(
        session_id="session_001",
        thread_id="thread_001",
        sender_type="human",
        sender_id="user_1",
        sender_name="玩家",
        content="你好",
    )
    assert result.content == "你好"


def test_conversation_get_messages():
    """ConversationService.get_messages 获取消息列表"""
    from api.services.conversation_service import ConversationService

    db = Mock()
    service = ConversationService(db)
    service.repo = Mock()
    service.repo.get_messages = Mock(return_value=[Mock(id="msg_001"), Mock(id="msg_002")])

    result = service.get_messages("session_001", thread_id="thread_001", limit=10)
    assert len(result) == 2


def test_conversation_get_threads():
    """ConversationService.get_threads 获取线程列表"""
    from api.services.conversation_service import ConversationService

    db = Mock()
    service = ConversationService(db)
    service.repo = Mock()
    service.repo.get_threads = Mock(return_value=[Mock(id="thread_001")])

    result = service.get_threads("session_001")
    assert len(result) == 1


# ---------------------------------------------------------------------------
# 7. 证物系统
# ---------------------------------------------------------------------------
def test_evidence_get_evidences():
    """EvidenceService.get_evidences 获取证物列表"""
    from api.services.evidence_service import EvidenceService

    db = Mock()
    service = EvidenceService(db)
    service.repo = Mock()
    service.repo.get_by_session = Mock(return_value=[Mock(id="ev_001"), Mock(id="ev_002")])

    result = service.get_evidences("session_001")
    assert len(result) == 2


def test_evidence_discover():
    """EvidenceService.discover_evidence 发现证物"""
    from api.services.evidence_service import EvidenceService

    db = Mock()
    service = EvidenceService(db)
    service.repo = Mock()

    mock_evidence = Mock()
    mock_evidence.id = "ev_001"
    mock_evidence.session_id = "session_001"
    mock_evidence.discovery_state = "hidden"
    service.repo.get_by_id = Mock(return_value=mock_evidence)
    service.repo.update = Mock(return_value=mock_evidence)

    result = service.discover_evidence("session_001", "ev_001")
    assert result.discovery_state == "discovered"


def test_evidence_discover_not_found():
    """EvidenceService.discover_evidence 证物不存在时抛异常"""
    from api.services.evidence_service import EvidenceService

    db = Mock()
    service = EvidenceService(db)
    service.repo = Mock()
    service.repo.get_by_id = Mock(return_value=None)

    try:
        service.discover_evidence("session_001", "nonexistent")
        assert False, "应该抛出 ValueError"
    except ValueError:
        pass


def test_evidence_discover_wrong_session():
    """EvidenceService.discover_evidence 证物不属于该会话时抛异常"""
    from api.services.evidence_service import EvidenceService

    db = Mock()
    service = EvidenceService(db)
    service.repo = Mock()

    mock_evidence = Mock()
    mock_evidence.id = "ev_001"
    mock_evidence.session_id = "session_other"
    service.repo.get_by_id = Mock(return_value=mock_evidence)

    try:
        service.discover_evidence("session_001", "ev_001")
        assert False, "应该抛出 ValueError"
    except ValueError:
        pass


def test_evidence_present():
    """EvidenceService.present_evidence 出示证物"""
    from api.services.evidence_service import EvidenceService

    db = Mock()
    service = EvidenceService(db)
    service.repo = Mock()

    mock_evidence = Mock()
    mock_evidence.id = "ev_001"
    mock_evidence.session_id = "session_001"
    mock_evidence.visibility = "private"
    mock_evidence.is_public = False
    mock_evidence.metadata_json = {}
    service.repo.get_by_id = Mock(return_value=mock_evidence)
    service.repo.update = Mock(return_value=mock_evidence)

    result = service.present_evidence("session_001", "ev_001", "char_001", is_public=True)
    assert result.visibility == "public"
    assert result.is_public is True


def test_evidence_get_public():
    """EvidenceService.get_public_evidences 获取公开证物"""
    from api.services.evidence_service import EvidenceService

    db = Mock()
    service = EvidenceService(db)
    service.repo = Mock()
    service.repo.get_public_by_session = Mock(return_value=[Mock(id="ev_001")])

    result = service.get_public_evidences("session_001")
    assert len(result) == 1


# ---------------------------------------------------------------------------
# 8. 投票和复盘
# ---------------------------------------------------------------------------
def test_review_service_run_review():
    """ReviewService.run_review 触发复盘生成"""
    from api.services.review_service import ReviewService

    db = Mock()
    service = ReviewService(db)
    service.repo = Mock()

    mock_review = Mock()
    mock_review.id = "review_001"
    mock_review.session_id = "session_001"
    mock_review.status = "pending"
    service.repo.get_by_session = Mock(return_value=None)
    service.repo.create = Mock(return_value=mock_review)
    service.repo.update = Mock(return_value=mock_review)

    result = service.run_review("session_001")
    assert result["status"] == "generating"
    assert result["session_id"] == "session_001"


def test_review_service_get_review():
    """ReviewService.get_review 获取复盘报告"""
    from api.services.review_service import ReviewService

    db = Mock()
    service = ReviewService(db)
    service.repo = Mock()

    mock_review = Mock()
    mock_review.id = "review_001"
    service.repo.get_by_session = Mock(return_value=mock_review)

    result = service.get_review("session_001")
    assert result is not None
    assert result.id == "review_001"


def test_review_service_get_review_not_found():
    """ReviewService.get_review 无复盘时返回 None"""
    from api.services.review_service import ReviewService

    db = Mock()
    service = ReviewService(db)
    service.repo = Mock()
    service.repo.get_by_session = Mock(return_value=None)

    result = service.get_review("nonexistent")
    assert result is None


# ---------------------------------------------------------------------------
# 9. 会话快照（集成流程）
# ---------------------------------------------------------------------------
def test_session_snapshot():
    """SessionService.get_snapshot 返回完整快照"""
    from api.services.session_service import SessionService

    db = Mock()
    service = SessionService(db)
    service.repo = Mock()

    mock_session = Mock()
    mock_session.id = "session_001"
    mock_session.script_id = "script_001"
    mock_session.current_phase = "investigation"
    mock_session.status = "active"

    service.repo.get_by_id = Mock(return_value=mock_session)
    service.repo.get_phase_events = Mock(return_value=[Mock(id="phase_001")])
    service.repo.get_casts = Mock(return_value=[Mock(id="cast_001")])

    result = service.get_snapshot("session_001")
    assert result is not None
    assert result["session"].id == "session_001"
    assert len(result["phase_events"]) == 1
    assert len(result["casts"]) == 1


def test_end_session():
    """SessionService.end_session 结束会话"""
    from api.services.session_service import SessionService

    db = Mock()
    service = SessionService(db)
    service.repo = Mock()

    mock_session = Mock()
    mock_session.id = "session_001"
    mock_session.status = "active"
    service.repo.get_by_id = Mock(return_value=mock_session)
    service.repo.update = Mock(return_value=mock_session)

    result = service.end_session("session_001")
    assert result.status == "ended"


# ---------------------------------------------------------------------------
# 10. 统一响应格式
# ---------------------------------------------------------------------------
def test_success_response_format():
    """success_response 返回标准格式"""
    from api.core.responses import success_response

    result = success_response(data={"key": "value"}, message="ok")
    assert result["success"] is True
    assert result["data"] == {"key": "value"}
    assert result["message"] == "ok"


def test_error_response_format():
    """error_response 返回标准错误格式"""
    from api.core.responses import error_response
    import json

    result = error_response(code="TEST_ERROR", message="测试错误", status_code=422)
    assert result.status_code == 422
    data = json.loads(result.body)
    assert data["success"] is False
    assert data["error"]["code"] == "TEST_ERROR"
    assert data["error"]["message"] == "测试错误"
