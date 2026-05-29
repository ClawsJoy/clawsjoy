#!/usr/bin/env python3
"""用户1 管理员工具"""

import requests
import json

BASE_URL = "https://localhost"
DRIVER_PORT = 5443
AUTH_PORT = 5444

def login():
    """登录获取 token"""
    resp = requests.post(
        f"{BASE_URL}:{AUTH_PORT}/auth/login",
        json={"user_id": "user1", "password": "admin123"},
        verify=False
    )
    if resp.status_code == 200:
        return resp.json().get('token')
    return None

def get_desensitization_rules(token):
    """获取脱敏规则"""
    resp = requests.get(
        f"{BASE_URL}:{DRIVER_PORT}/api/driver/config/desensitization",
        headers={"Authorization": f"Bearer {token}"},
        verify=False
    )
    return resp.json()

if __name__ == "__main__":
    print("用户1 管理员工具")
    print("=" * 40)
    
    token = login()
    if token:
        print("✅ 登录成功")
        rules = get_desensitization_rules(token)
        print(f"脱敏规则版本: {rules.get('version', 'N/A')}")
        print(f"敏感模式数: {len(rules.get('patterns', {}))}")
    else:
        print("❌ 登录失败")
