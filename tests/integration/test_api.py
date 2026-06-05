"""API 集成测试"""

import json

import pytest


class TestAPI:
    """API 测试"""

    def test_health_endpoint(self, client):
        """测试健康检查端点"""
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"

    def test_skills_list(self, client):
        """测试技能列表端点"""
        response = client.get("/api/skills/list")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "total" in data

    def test_agents_list(self, client):
        """测试 Agent 列表端点"""
        response = client.get("/api/agents/list")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "agents" in data

    def test_enhanced_chat_greeting(self, client):
        """测试对话 - 问候"""
        response = client.post(
            "/api/v5/enhanced/chat", json={"message": "你好", "user_id": "test_user"}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "response" in data

    def test_enhanced_chat_code(self, client):
        """测试对话 - 代码"""
        response = client.post(
            "/api/v5/enhanced/chat",
            json={"message": "写一个排序函数", "user_id": "test_user"},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get("agent") == "code_agent"

    def test_enhanced_chat_weather(self, client):
        """测试对话 - 天气"""
        response = client.post(
            "/api/v5/enhanced/chat",
            json={"message": "北京天气", "user_id": "test_user"},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get("agent") in ["atomic_skill", "weather_skill", "chat_agent"]

    def test_enhanced_chat_translate(self, client):
        """测试对话 - 翻译"""
        response = client.post(
            "/api/v5/enhanced/chat",
            json={"message": "把hello翻译成中文", "user_id": "test_user"},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        # 翻译可能走 translate_agent 或 chat_agent
        assert data.get("agent") in ["translate_agent", "chat_agent"]

    def test_memory_remember(self, client):
        """测试记忆存储"""
        response = client.post(
            "/api/v5/memory/remember", json={"user_id": "test_user", "fact": "测试记忆"}
        )
        assert response.status_code == 200

    def test_memory_recall(self, client):
        """测试记忆回忆"""
        response = client.post(
            "/api/v5/memory/recall", json={"user_id": "test_user", "query": "测试"}
        )
        assert response.status_code == 200
