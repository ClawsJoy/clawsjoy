"""修复后的 API 测试（带认证）"""

import pytest
import requests

BASE_URL = "http://localhost:5002"


class TestAPIWithAuth:
    
    def test_health_endpoint(self):
        """健康检查不需要认证"""
        resp = requests.get(f"{BASE_URL}/health")
        assert resp.status_code == 200
    
    def test_skills_list(self, auth_headers):
        """技能列表需要认证"""
        resp = requests.get(f"{BASE_URL}/api/skills/list", headers=auth_headers)
        assert resp.status_code == 200
    
    def test_agents_list(self, auth_headers):
        """Agent 列表需要认证"""
        resp = requests.get(f"{BASE_URL}/api/agents/list", headers=auth_headers)
        assert resp.status_code == 200
    
    def test_enhanced_chat_greeting(self, auth_headers):
        """对话测试"""
        resp = requests.post(
            f"{BASE_URL}/api/v5/enhanced/chat",
            json={"user_id": "test", "message": "你好"},
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") == True
    
    def test_enhanced_chat_calculate(self, auth_headers):
        """计算测试"""
        resp = requests.post(
            f"{BASE_URL}/api/v5/enhanced/chat",
            json={"user_id": "test", "message": "计算 1+1"},
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") == True
    
    def test_enhanced_chat_translate_short(self, auth_headers):
        """短翻译测试"""
        resp = requests.post(
            f"{BASE_URL}/api/v5/enhanced/chat",
            json={"user_id": "test", "message": "翻译 hello"},
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") == True
    
    def test_enhanced_chat_translate_long(self, auth_headers):
        """长翻译测试（应走 C 路由）"""
        resp = requests.post(
            f"{BASE_URL}/api/v5/enhanced/chat",
            json={"user_id": "test", "message": "翻译 这是一段用来测试长文本翻译功能的非常长的文本内容"},
            headers=auth_headers
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("success") == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
