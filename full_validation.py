#!/usr/bin/env python3
"""ClawsJoy v5 完整功能验证"""

import json
import sys
import time

import requests

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

BASE_URL = "http://127.0.0.1:5002"
TEST_USER = "validation_user"

print("=" * 60)
print("🔬 ClawsJoy v5 完整功能验证")
print("=" * 60)

results = {"pass": 0, "fail": 0, "total": 0}


def test(name, func):
    global results
    results["total"] += 1
    print(f"\n📝 测试: {name}")
    try:
        func()
        print(f"   ✅ 通过")
        results["pass"] += 1
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        results["fail"] += 1


# ============================================================
# 1. 基础服务验证
# ============================================================
def test_health():
    resp = requests.get(f"{BASE_URL}/health", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    print(f"      version: {data['version']}")


def test_metrics():
    resp = requests.get(f"{BASE_URL}/metrics", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    assert "cpu_percent" in data
    print(f"      cpu: {data['cpu_percent']}%, mem: {data['memory_percent']}%")


# ============================================================
# 2. Agent 功能验证
# ============================================================
def test_chat_agent():
    resp = requests.post(
        f"{BASE_URL}/api/v5/enhanced/chat",
        json={"user_id": TEST_USER, "message": "你好"},
        timeout=30,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] == True
    assert "response" in data
    print(f"      response: {data['response'][:50]}...")


def test_calculation():
    resp = requests.post(
        f"{BASE_URL}/api/v5/enhanced/chat",
        json={"user_id": TEST_USER, "message": "1+2等于多少"},
        timeout=30,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] == True
    assert "3" in data["response"] or "3" in str(data["response"])
    print(f"      result: {data['response'][:50]}")


def test_weather():
    resp = requests.post(
        f"{BASE_URL}/api/v5/enhanced/chat",
        json={"user_id": TEST_USER, "message": "今天天气怎么样"},
        timeout=30,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] == True
    print(f"      response: {data['response'][:50]}")


# ============================================================
# 3. 缓存系统验证
# ============================================================
def test_cache_first():
    # 清除缓存统计
    requests.get(f"{BASE_URL}/api/v5/stats/cache")

    resp = requests.post(
        f"{BASE_URL}/api/v5/enhanced/chat",
        json={"user_id": "cache_test", "message": "缓存测试消息"},
        timeout=30,
    )
    data = resp.json()
    # 第一次请求不应该有 cached 字段
    assert "cached" not in data or data.get("cached") != True
    print(f"      第一次请求: agent={data.get('agent', 'unknown')}")


def test_cache_second():
    resp = requests.post(
        f"{BASE_URL}/api/v5/enhanced/chat",
        json={"user_id": "cache_test", "message": "缓存测试消息"},
        timeout=30,
    )
    data = resp.json()
    assert data.get("cached") == True
    print(f"      第二次请求: cached=true, agent={data.get('agent')}")


def test_cache_stats():
    resp = requests.get(f"{BASE_URL}/api/v5/stats/cache", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    print(
        f"      hit_count: {data['hit_count']}, miss_count: {data['miss_count']}, size: {data['size']}"
    )


# ============================================================
# 4. 记忆系统验证
# ============================================================
def test_memory_remember():
    resp = requests.post(
        f"{BASE_URL}/api/v5/memory/remember",
        json={"user_id": TEST_USER, "fact": "用户喜欢Python"},
        timeout=10,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("success") == True
    print(f"      记忆已存储")


def test_memory_recall():
    resp = requests.post(
        f"{BASE_URL}/api/v5/memory/recall",
        json={"user_id": TEST_USER, "limit": 5},
        timeout=10,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("success") == True
    print(f"      检索到 {len(data.get('results', []))} 条记忆")


def test_memory_stats():
    resp = requests.get(
        f"{BASE_URL}/api/v5/memory/stats?user_id={TEST_USER}", timeout=10
    )
    assert resp.status_code == 200
    data = resp.json()
    print(f"      记忆统计: {data.get('total', 0)} 条")


# ============================================================
# 5. 健康检查验证
# ============================================================
def test_detailed_health():
    resp = requests.get(f"{BASE_URL}/api/v5/health/detailed", timeout=10)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("database", {}).get("status") in ["healthy", "degraded"]
    assert data.get("memory", {}).get("status") in ["healthy", "warning"]
    print(
        f"      数据库: {data['database']['status']}, 内存: {data['memory']['status']}"
    )


# ============================================================
# 6. 性能统计验证
# ============================================================
def test_performance_stats():
    resp = requests.get(f"{BASE_URL}/api/v5/stats/performance", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    print(
        f"      total_requests: {data['total_requests']}, slow_requests: {data['slow_requests']}"
    )


def test_ratelimit_stats():
    resp = requests.get(f"{BASE_URL}/api/v5/stats/ratelimit", timeout=5)
    assert resp.status_code == 200
    data = resp.json()
    print(f"      limit: {data['limit']}/min, current: {data['current_requests']}")


# ============================================================
# 7. 限流验证
# ============================================================
def test_rate_limit():
    """快速发送61个请求，测试限流"""
    success = 0
    limited = 0
    for i in range(65):
        resp = requests.post(
            f"{BASE_URL}/api/v5/enhanced/chat",
            json={"user_id": f"rate_test_{i}", "message": f"测试{i}"},
            timeout=10,
        )
        if resp.status_code == 429:
            limited += 1
        elif resp.status_code == 200:
            success += 1
        if i > 60:
            break
    print(f"      成功: {success}, 限流: {limited}")
    # 限流应该生效
    assert limited > 0 or success < 61


# ============================================================
# 运行所有测试
# ============================================================
if __name__ == "__main__":
    test("1. 健康检查", test_health)
    test("2. 监控指标", test_metrics)
    test("3. Chat Agent", test_chat_agent)
    test("4. 数学计算", test_calculation)
    test("5. 天气查询", test_weather)
    test("6. 缓存 - 第一次请求", test_cache_first)
    test("7. 缓存 - 第二次请求", test_cache_second)
    test("8. 缓存统计", test_cache_stats)
    test("9. 记忆存储", test_memory_remember)
    test("10. 记忆检索", test_memory_recall)
    test("11. 记忆统计", test_memory_stats)
    test("12. 详细健康检查", test_detailed_health)
    test("13. 性能统计", test_performance_stats)
    test("14. 限流统计", test_ratelimit_stats)
    test("15. 限流验证", test_rate_limit)

    print("\n" + "=" * 60)
    print(f"📊 测试结果: {results['pass']}/{results['total']} 通过")
    print("=" * 60)

    if results["pass"] == results["total"]:
        print("🎉 所有测试通过！系统功能完整！")
    else:
        print(f"⚠️ {results['fail']} 个测试失败，需要检查")
