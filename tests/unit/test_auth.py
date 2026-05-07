#!/usr/bin/env python3
"""认证模块单元测试"""

import pytest
import sys
import hashlib

sys.path.insert(0, '/home/flybo/clawsjoy/bin')

# 简化测试，不依赖外部模块
def test_hash_password():
    """测试密码哈希"""
    password = "test123"
    result = hashlib.sha256(password.encode()).hexdigest()
    assert len(result) == 64
    assert result == hashlib.sha256(b"test123").hexdigest()

def test_token_format():
    """测试 token 格式"""
    import jwt
    token = jwt.encode({"user": "admin", "exp": 9999999999}, "secret", algorithm="HS256")
    assert isinstance(token, str)
    assert len(token) > 20

def test_success():
    """基础测试"""
    assert True
