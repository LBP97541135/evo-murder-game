# -*- coding: utf-8 -*-
"""Skill 服务单元测试

覆盖 Skill 的 CRUD、搜索、注入、导入导出等核心功能。
"""
from unittest.mock import Mock, MagicMock
from datetime import datetime


def test_create_skill():
    """测试创建 Skill"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()

    mock_skill = Mock()
    mock_skill.id = "skill_001"
    mock_skill.name = "测试 Skill"
    mock_skill.category = "hosting"
    mock_skill.status = "active"
    service.repo.create = Mock(return_value=mock_skill)

    result = service.create_skill({
        "name": "测试 Skill",
        "category": "hosting",
        "applicable_roles": ["dm"],
        "signals": ["控场", "节奏"],
    })
    assert result is not None
    assert result.name == "测试 Skill"
    assert result.category == "hosting"
    service.repo.create.assert_called_once()


def test_get_skill():
    """测试获取单个 Skill"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()

    mock_skill = Mock()
    mock_skill.id = "skill_001"
    mock_skill.name = "测试 Skill"
    service.repo.get_by_id = Mock(return_value=mock_skill)

    result = service.get_skill("skill_001")
    assert result is not None
    assert result.id == "skill_001"


def test_get_skill_not_found():
    """测试获取不存在的 Skill"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()
    service.repo.get_by_id = Mock(return_value=None)

    result = service.get_skill("nonexistent")
    assert result is None


def test_list_skills():
    """测试列出 Skill"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()
    service.repo.list = Mock(return_value=[
        Mock(id="skill_001", name="Skill 1"),
        Mock(id="skill_002", name="Skill 2"),
    ])

    result = service.list_skills()
    assert isinstance(result, list)
    assert len(result) == 2


def test_list_skills_by_category():
    """测试按分类列出 Skill"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()
    service.repo.list = Mock(return_value=[Mock(id="skill_001")])

    result = service.list_skills(category="hosting")
    assert len(result) == 1
    service.repo.list.assert_called_with(category="hosting", status=None)


def test_list_skills_by_status():
    """测试按状态列出 Skill"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()
    service.repo.list = Mock(return_value=[Mock(id="skill_001")])

    result = service.list_skills(status="active")
    assert len(result) == 1
    service.repo.list.assert_called_with(category=None, status="active")


def test_search_skills():
    """测试搜索 Skill"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()
    service.repo.search = Mock(return_value=[
        Mock(id="skill_001", name="DM 控场技巧"),
    ])

    result = service.search_skills(role="dm", category="hosting", limit=5)
    assert isinstance(result, list)
    assert len(result) == 1
    service.repo.search.assert_called_with(role="dm", category="hosting", signals=None, limit=5)


def test_search_skills_with_signals():
    """测试使用信号关键词搜索 Skill"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()
    service.repo.search = Mock(return_value=[Mock(id="skill_001")])

    result = service.search_skills(signals=["控场", "节奏"], limit=10)
    assert len(result) == 1
    service.repo.search.assert_called_with(role=None, category=None, signals=["控场", "节奏"], limit=10)


def test_update_skill():
    """测试更新 Skill"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()

    mock_skill = Mock()
    mock_skill.id = "skill_001"
    mock_skill.name = "旧名称"
    mock_skill.description = "旧描述"
    service.repo.get_by_id = Mock(return_value=mock_skill)
    service.repo.update = Mock(return_value=mock_skill)

    result = service.update_skill("skill_001", {
        "name": "新名称",
        "description": "新描述",
    })
    assert result.name == "新名称"
    assert result.description == "新描述"
    assert result.updated_at is not None


def test_update_skill_not_found():
    """测试更新不存在的 Skill 抛出异常"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()
    service.repo.get_by_id = Mock(return_value=None)

    try:
        service.update_skill("nonexistent", {"name": "新名称"})
        assert False, "应该抛出 ValueError"
    except ValueError as e:
        assert "不存在" in str(e)


def test_delete_skill():
    """测试删除 Skill"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()
    service.repo.delete = Mock(return_value=True)

    result = service.delete_skill("skill_001")
    assert result is True
    service.repo.delete.assert_called_with("skill_001")


def test_delete_skill_not_found():
    """测试删除不存在的 Skill 返回 False"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()
    service.repo.delete = Mock(return_value=False)

    result = service.delete_skill("nonexistent")
    assert result is False


def test_inject_skills():
    """测试 Skill 注入逻辑"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()

    mock_skill_1 = Mock()
    mock_skill_1.prompt_content = "这是 DM 控场技巧 1"
    mock_skill_2 = Mock()
    mock_skill_2.prompt_content = "这是 DM 控场技巧 2"
    service.repo.search = Mock(return_value=[mock_skill_1, mock_skill_2])

    result = service.inject_skills("session_001", "agent_001", "dm", "investigation")
    assert "DM 控场技巧 1" in result
    assert "DM 控场技巧 2" in result
    assert "\n\n" in result


def test_inject_skills_no_match():
    """测试无匹配 Skill 时注入返回空字符串"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()
    service.repo.search = Mock(return_value=[])

    result = service.inject_skills("session_001", "agent_001", "dm", "investigation")
    assert result == ""


def test_inject_skills_empty_prompt():
    """测试 Skill 的 prompt_content 为空时跳过"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()

    mock_skill_1 = Mock()
    mock_skill_1.prompt_content = "有效内容"
    mock_skill_2 = Mock()
    mock_skill_2.prompt_content = ""
    service.repo.search = Mock(return_value=[mock_skill_1, mock_skill_2])

    result = service.inject_skills("session_001", "agent_001", "dm", "investigation")
    assert result == "有效内容"


def test_record_usage():
    """测试记录 Skill 使用情况"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()

    mock_log = Mock()
    mock_log.id = "log_001"
    mock_log.skill_id = "skill_001"
    mock_log.session_id = "session_001"
    mock_log.agent_id = "agent_001"
    mock_log.phase = "investigation"
    mock_log.injection_tokens = 500
    service.repo.create_usage_log = Mock(return_value=mock_log)

    result = service.record_usage("skill_001", "session_001", "agent_001", "investigation", 500)
    assert result.skill_id == "skill_001"
    assert result.injection_tokens == 500


def test_create_experience():
    """测试创建经验记录"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()

    mock_exp = Mock()
    mock_exp.id = "exp_001"
    mock_exp.session_id = "session_001"
    mock_exp.role = "dm"
    mock_exp.category = "hosting"
    mock_exp.self_score = 8.5
    service.repo.create_experience = Mock(return_value=mock_exp)

    result = service.create_experience({
        "session_id": "session_001",
        "role": "dm",
        "category": "hosting",
        "self_score": 8.5,
        "summary": "控场良好",
    })
    assert result.self_score == 8.5
    assert result.role == "dm"


def test_get_experiences():
    """测试获取经验记录列表"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()
    service.repo.get_experiences = Mock(return_value=[
        Mock(id="exp_001"),
        Mock(id="exp_002"),
    ])

    result = service.get_experiences(session_id="session_001")
    assert len(result) == 2


def test_generate_skill_from_experience():
    """测试从经验记录生成 Skill"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()

    mock_exp = Mock()
    mock_exp.id = "exp_001"
    mock_exp.summary = "这是一段很好的控场经验"
    mock_exp.detail = "详细内容..."
    mock_exp.category = "hosting"
    mock_exp.role = "dm"
    mock_exp.signals = ["控场", "节奏"]
    mock_exp.session_id = "session_001"
    mock_exp.script_id = "script_001"
    service.repo.get_experience = Mock(return_value=mock_exp)

    mock_skill = Mock()
    mock_skill.id = "skill_001"
    mock_skill.source_type = "experience"
    mock_skill.source_experience_id = "exp_001"
    service.repo.create = Mock(return_value=mock_skill)

    result = service.generate_skill_from_experience("exp_001")
    assert result.source_type == "experience"
    assert result.source_experience_id == "exp_001"


def test_generate_skill_from_nonexistent_experience():
    """测试从不存在的经验记录生成 Skill 抛出异常"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()
    service.repo.get_experience = Mock(return_value=None)

    try:
        service.generate_skill_from_experience("nonexistent")
        assert False, "应该抛出 ValueError"
    except ValueError as e:
        assert "不存在" in str(e)


def test_export_skill():
    """测试导出 Skill"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()

    mock_skill = Mock()
    mock_skill.id = "skill_001"
    mock_skill.name = "测试 Skill"
    mock_skill.version = "1.0.0"
    mock_skill.type = "prompt_skill"
    mock_skill.category = "hosting"
    mock_skill.applicable_roles = ["dm"]
    mock_skill.signals = ["控场"]
    mock_skill.description = "描述"
    mock_skill.prompt_content = "内容"
    mock_skill.strategy = "策略"
    mock_skill.examples = "示例"
    mock_skill.anti_patterns = "反模式"
    mock_skill.injection_mode = "append_system_prompt"
    mock_skill.injection_priority = 50
    mock_skill.max_tokens = 800
    mock_skill.metadata_json = {"key": "value"}
    service.repo.get_by_id = Mock(return_value=mock_skill)

    result = service.export_skill("skill_001")
    assert result["id"] == "skill_001"
    assert result["name"] == "测试 Skill"
    assert result["metadata"] == {"key": "value"}


def test_export_skill_not_found():
    """测试导出不存在的 Skill 抛出异常"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()
    service.repo.get_by_id = Mock(return_value=None)

    try:
        service.export_skill("nonexistent")
        assert False, "应该抛出 ValueError"
    except ValueError as e:
        assert "不存在" in str(e)


def test_import_skill():
    """测试导入 Skill"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()

    mock_skill = Mock()
    mock_skill.id = "skill_001"
    mock_skill.name = "导入的 Skill"
    service.repo.create = Mock(return_value=mock_skill)

    result = service.import_skill({
        "name": "导入的 Skill",
        "category": "hosting",
        "prompt_content": "内容",
    })
    assert result.name == "导入的 Skill"
