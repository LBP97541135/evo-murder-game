# -*- coding: utf-8 -*-
"""会话服务单元测试"""
from unittest.mock import Mock


def test_create_session():
    """测试创建游戏会话"""
    from api.services.session_service import SessionService

    db = Mock()
    service = SessionService(db)
    service.repo = Mock()

    mock_session = Mock()
    mock_session.id = "session_001"
    mock_session.script_id = "script_001"
    mock_session.status = "active"
    service.repo.create = Mock(return_value=mock_session)

    result = service.create_session({"script_id": "script_001", "title": "测试会话"})
    assert result is not None
    assert result.script_id == "script_001"


def test_get_snapshot():
    """测试获取游戏快照"""
    from api.services.session_service import SessionService

    db = Mock()
    service = SessionService(db)
    service.repo = Mock()

    mock_session = Mock()
    mock_session.id = "session_001"
    mock_session.script_id = "script_001"
    mock_session.current_phase = "investigation"
    mock_session.status = "active"
    mock_session.title = "测试会话"

    service.repo.get_by_id = Mock(return_value=mock_session)
    service.repo.get_casts = Mock(return_value=[])
    service.repo.get_phase_events = Mock(return_value=[])

    result = service.get_snapshot("session_001")
    assert result is not None
    assert result["session"].id == "session_001"


def test_get_snapshot_not_found():
    """测试获取不存在的会话快照"""
    from api.services.session_service import SessionService

    db = Mock()
    service = SessionService(db)
    service.repo = Mock()
    service.repo.get_by_id = Mock(return_value=None)

    result = service.get_snapshot("nonexistent")
    assert result is None


def test_end_session():
    """测试结束游戏会话"""
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
    assert result is not None
    assert mock_session.status == "ended"
