"""pytest 配置和共享 fixtures"""

import sys
from pathlib import Path

import pytest

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def app():
    """Flask 应用 fixture"""
    from agent_gateway_enhanced import app

    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """测试客户端 fixture"""
    return app.test_client()


@pytest.fixture
def sample_user_id():
    """测试用户 ID"""
    return "test_user_001"


@pytest.fixture
def sample_message():
    """测试消息"""
    return "你好，我是测试用户"


@pytest.fixture
def engine():
    """原子引擎 fixture"""
    from engine import engine

    return engine
