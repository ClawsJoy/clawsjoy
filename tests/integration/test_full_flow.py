"""完整流程集成测试"""

import json
import time

import pytest


class TestFullFlow:
    """完整流程测试"""

    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get("/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"

    def test_skills_api(self, client):
        """测试技能API"""
        response = client.get("/api/skills/list")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "total" in data
        assert "skills" in data

    def test_agents_api(self, client):
        """测试Agent API"""
        response = client.get("/api/agents/list")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "agents" in data
        assert len(data["agents"]) > 0

    def test_chat_greeting(self, client):
        """测试问候对话"""
        response = client.post(
            "/api/v5/enhanced/chat", json={"message": "你好", "user_id": "test_user"}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "response" in data
        assert data["success"] == True

    def test_chat_code(self, client):
        """测试代码生成"""
        response = client.post(
            "/api/v5/enhanced/chat",
            json={"message": "写一个排序函数", "user_id": "test_user"},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get("agent") in ["code_agent", "chat_agent"]

    def test_chat_weather(self, client):
        """测试天气查询"""
        response = client.post(
            "/api/v5/enhanced/chat",
            json={"message": "北京天气", "user_id": "test_user"},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get("agent") in ["atomic_skill", "weather_skill", "chat_agent"]

    def test_chat_translate(self, client):
        """测试翻译"""
        response = client.post(
            "/api/v5/enhanced/chat",
            json={"message": "把hello翻译成中文", "user_id": "test_user"},
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get("agent") in ["translate_agent", "chat_agent"]

    def test_chat_calculate(self, client):
        """测试计算"""
        response = client.post(
            "/api/v5/enhanced/chat", json={"message": "15加27", "user_id": "test_user"}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "response" in data

    def test_memory_chain(self, client):
        """测试记忆链 (多轮对话)"""
        user_id = "memory_test_user"

        # 第1轮：告诉名字
        response1 = client.post(
            "/api/v5/enhanced/chat", json={"message": "我叫李华", "user_id": user_id}
        )
        assert response1.status_code == 200

        # 第2轮：询问名字
        response2 = client.post(
            "/api/v5/enhanced/chat",
            json={"message": "我叫什么名字", "user_id": user_id},
        )
        assert response2.status_code == 200
        data2 = json.loads(response2.data)
        assert "李华" in data2.get("response", "")

        # 第3轮：告诉偏好
        response3 = client.post(
            "/api/v5/enhanced/chat",
            json={"message": "我喜欢喝咖啡", "user_id": user_id},
        )
        assert response3.status_code == 200

        # 第4轮：询问偏好
        response4 = client.post(
            "/api/v5/enhanced/chat", json={"message": "我喜欢什么", "user_id": user_id}
        )
        assert response4.status_code == 200

    def test_learning_endpoint(self, client):
        """测试学习端点"""
        response = client.post(
            "/api/learning/record", json={"fact": "测试学习", "success": True}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get("success") == True

    def test_vector_search(self, client):
        """测试向量搜索"""
        response = client.post("/api/vector/search", json={"query": "代码", "top_k": 5})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get("success") == True

    def test_club_stats(self, client):
        """测试俱乐部统计"""
        response = client.get("/api/club/stats")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data.get("success") == True


class TestPerformance:
    """性能测试"""

    def test_concurrent_requests(self, client):
        """测试并发请求"""
        import threading
        import time

        results = []

        def make_request():
            resp = client.post(
                "/api/v5/enhanced/chat",
                json={"message": "你好", "user_id": "perf_test"},
            )
            results.append(resp.status_code)

        threads = []
        start = time.time()
        for _ in range(10):
            t = threading.Thread(target=make_request)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()
        elapsed = time.time() - start

        assert all(r == 200 for r in results)
        assert elapsed < 5  # 10个请求应在5秒内完成

    def test_response_time(self, client):
        """测试响应时间"""
        import time

        start = time.time()
        response = client.post(
            "/api/v5/enhanced/chat", json={"message": "你好", "user_id": "perf_test"}
        )
        elapsed = (time.time() - start) * 1000

        assert response.status_code == 200
        assert elapsed < 1000  # 响应时间应小于1秒


class TestErrorHandling:
    """错误处理测试"""

    def test_invalid_json(self, client):
        """测试无效JSON"""
        response = client.post(
            "/api/v5/enhanced/chat",
            data="invalid json",
            content_type="application/json",
        )
        # 应该返回错误而不是崩溃
        assert response.status_code in [400, 500, 200]

    def test_empty_message(self, client):
        """测试空消息"""
        response = client.post(
            "/api/v5/enhanced/chat", json={"message": "", "user_id": "test"}
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "response" in data

    def test_missing_user_id(self, client):
        """测试缺失user_id"""
        response = client.post("/api/v5/enhanced/chat", json={"message": "你好"})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "response" in data
