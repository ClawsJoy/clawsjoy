"""pytest 配置和共享 fixtures"""

import pytest
import requests
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def auth_token():
    """获取认证 token"""
    # 先注册用户
    requests.post(
        "http://localhost:5002/api/user/register",
        json={"username": "testuser", "password": "test123"}
    )
    
    # 登录获取 token
    resp = requests.post(
        "http://localhost:5002/api/user/login",
        json={"username": "testuser", "password": "test123"}
    )
    if resp.status_code == 200:
        return resp.json().get("token")
    return None


@pytest.fixture
def auth_headers(auth_token):
    """认证请求头"""
    return {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
