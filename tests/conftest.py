#!/usr/bin/env python3
"""pytest 共享配置"""

import pytest
import requests
import time

@pytest.fixture(scope="session")
def base_url():
    """API 基础 URL"""
    return "http://localhost"

@pytest.fixture(scope="session")
def auth_token(base_url):
    """获取认证 token"""
    resp = requests.post(
        f"{base_url}:8092/api/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    assert resp.status_code == 200
    return resp.json().get("token")

@pytest.fixture(scope="session")
def tenant_id():
    """测试租户 ID"""
    return "1"

@pytest.fixture
def wait_for_service():
    """等待服务就绪"""
    def _wait(url, timeout=30):
        start = time.time()
        while time.time() - start < timeout:
            try:
                resp = requests.get(url, timeout=2)
                if resp.status_code < 500:
                    return True
            except:
                pass
            time.sleep(1)
        return False
    return _wait
