# -*- coding: utf-8 -*-
"""API 端点集成测试 + 乱码扫描测试

覆盖 /skills 路由的真实调用和 API 响应乱码检测。
使用 Mock 避免真实数据库写入。
"""
from unittest.mock import Mock, patch
import json


# ---------------------------------------------------------------------------
# P0-8: /skills API 端点测试
# ---------------------------------------------------------------------------

def test_skills_service_list_method_exists():
    """SkillRepository.list() 方法存在且可调用"""
    from api.repositories.skill_repository import SkillRepository
    assert hasattr(SkillRepository, 'list'), "SkillRepository must have list() method"


def test_skills_list_via_service():
    """SkillService.list_skills() 调用 repo.list() 而不报错"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()
    service.repo.list = Mock(return_value=[])

    result = service.list_skills()
    assert isinstance(result, list)
    service.repo.list.assert_called_once()


def test_skills_list_with_category():
    """SkillService.list_skills(category=...) 正确传递参数"""
    from api.services.skill_service import SkillService

    db = Mock()
    service = SkillService(db)
    service.repo = Mock()
    service.repo.list = Mock(return_value=[])

    service.list_skills(category="hosting", status="active")
    service.repo.list.assert_called_with(category="hosting", status="active")


# ---------------------------------------------------------------------------
# P0-9: API 响应乱码扫描测试
# ---------------------------------------------------------------------------

MOJIBAKE_CHARS = set('éåæèãçìë¯½ðïî')


def _scan_value_for_mojibake(value, path=""):
    """递归扫描 JSON 值中的乱码字符。"""
    issues = []
    if isinstance(value, str):
        for char in value:
            if char in MOJIBAKE_CHARS:
                issues.append(f"{path}: '{char}' in '{value[:60]}'")
                break
    elif isinstance(value, dict):
        for k, v in value.items():
            issues.extend(_scan_value_for_mojibake(v, f"{path}.{k}"))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            issues.extend(_scan_value_for_mojibake(v, f"{path}[{i}]"))
    return issues


def test_scripts_api_no_mojibake():
    """GET /scripts/ 响应中无乱码字符"""
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    response = client.get("/scripts/")
    assert response.status_code == 200
    data = response.json()
    issues = _scan_value_for_mojibake(data, "response")
    assert len(issues) == 0, f"Mojibake found in /scripts/: {issues}"


def test_skills_api_no_mojibake():
    """GET /skills/ 响应中无乱码字符"""
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    response = client.get("/skills/")
    assert response.status_code == 200
    data = response.json()
    issues = _scan_value_for_mojibake(data, "response")
    assert len(issues) == 0, f"Mojibake found in /skills/: {issues}"


def test_database_text_fields_no_mojibake():
    """数据库文本字段无乱码"""
    import sqlite3, os
    db_path = os.getenv("SQLITE_PATH", "data/murder_mystery.db")
    if not os.path.exists(db_path):
        return  # Skip if no database

    conn = sqlite3.connect(db_path)
    tables_to_check = [
        ('scripts', ['title', 'description']),
        ('script_characters', ['name', 'bio']),
        ('agents', ['name', 'identity_doc']),
        ('skills', ['name', 'prompt_content']),
    ]

    for table, columns in tables_to_check:
        try:
            col_list = ", ".join(f"[{c}]" for c in columns)
            rows = conn.execute(f"SELECT {col_list} FROM {table}").fetchall()
            for row in rows:
                for i, val in enumerate(row):
                    if isinstance(val, str):
                        for char in val:
                            assert char not in MOJIBAKE_CHARS, (
                                f"Mojibake in {table}.{columns[i]}: '{char}' in '{val[:60]}'"
                            )
        except sqlite3.OperationalError:
            pass  # Table might not exist

    conn.close()
