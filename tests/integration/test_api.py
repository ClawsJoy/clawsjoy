#!/usr/bin/env python3
"""API 集成测试"""

import requests
import pytest

BASE_URL = "http://localhost"

def test_auth_health():
    """认证服务健康检查"""
    resp = requests.get(f"{BASE_URL}:8092/api/auth/health", timeout=5)
    assert resp.status_code == 200
    assert resp.json().get("status") == "ok"

def test_auth_login():
    """认证登录测试"""
    resp = requests.post(
        f"{BASE_URL}:8092/api/auth/login",
        json={"username": "admin", "password": "admin123"},
        timeout=5
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("success") is True
    assert data.get("token") is not None

def test_tenant_list():
    """租户列表测试"""
    resp = requests.get(f"{BASE_URL}:8088/api/tenants", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("success") is True
    assert isinstance(data.get("tenants"), list)

def test_billing_balance():
    """计费余额测试"""
    resp = requests.get(f"{BASE_URL}:8090/api/billing/balance?tenant_id=1", timeout=5)
    assert resp.status_code == 200
    assert "balance" in resp.json()

def test_health_check():
    """健康检查汇总测试"""
    resp = requests.get(f"{BASE_URL}:8095/health", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("service") == "clawsjoy"
    assert "checks" in data

if __name__ == "__main__":
    # 手动运行测试
    test_auth_health()
    test_auth_login()
    test_tenant_list()
    test_billing_balance()
    test_health_check()
    print("✅ 所有集成测试通过")
