# -*- coding: utf-8 -*-
"""健康检查接口测试"""


def test_health_endpoint():
    """测试健康检查端点返回正确格式"""
    from fastapi.testclient import TestClient
    from api.main import app

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("success") is True


def test_success_response_format():
    """测试统一成功响应格式"""
    from api.core.responses import success_response

    result = success_response(data={"key": "value"}, message="测试")
    assert result["success"] is True
    assert result["data"] == {"key": "value"}
    assert result["message"] == "测试"


def test_error_response_format():
    """测试统一错误响应格式"""
    from api.core.responses import error_response

    result = error_response(code="TEST_ERROR", message="测试错误")
    assert result.status_code == 400
    import json
    data = json.loads(result.body)
    assert data["success"] is False
    assert data["error"]["code"] == "TEST_ERROR"
