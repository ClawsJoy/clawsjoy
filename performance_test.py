#!/usr/bin/env python3
"""性能压测脚本"""

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

BASE_URL = "http://127.0.0.1:5002"


def test_health():
    """健康检查测试"""
    start = time.time()
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        return resp.status_code == 200, time.time() - start
    except Exception as e:
        return False, 0


def test_chat():
    """聊天 API 测试"""
    start = time.time()
    try:
        resp = requests.post(
            f"{BASE_URL}/api/v5/enhanced/chat",
            json={"user_id": "perf_test", "message": "你好"},
            timeout=10,
        )
        return resp.status_code == 200, time.time() - start
    except Exception as e:
        return False, 0


def run_load_test(concurrent=10, total_requests=100):
    """负载测试"""
    print(f"\n🚀 负载测试: {concurrent} 并发, {total_requests} 请求")

    success_count = 0
    response_times = []

    with ThreadPoolExecutor(max_workers=concurrent) as executor:
        futures = []
        for i in range(total_requests):
            futures.append(executor.submit(test_chat))

        for future in as_completed(futures):
            success, duration = future.result()
            if success:
                success_count += 1
                response_times.append(duration)

    print(
        f"   ✅ 成功率: {success_count}/{total_requests} ({success_count/total_requests*100:.1f}%)"
    )
    if response_times:
        print(f"   ⏱️  平均响应: {sum(response_times)/len(response_times)*1000:.1f} ms")
        print(f"   ⏱️  最快响应: {min(response_times)*1000:.1f} ms")
        print(f"   ⏱️  最慢响应: {max(response_times)*1000:.1f} ms")


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 ClawsJoy v5 性能测试")
    print("=" * 50)

    # 预热
    print("\n🔥 预热...")
    for _ in range(5):
        test_health()
    time.sleep(1)

    # 单次测试
    print("\n📝 单次请求测试...")
    success, duration = test_chat()
    print(f"   耗时: {duration*1000:.1f} ms")

    # 负载测试
    run_load_test(concurrent=5, total_requests=50)
    run_load_test(concurrent=10, total_requests=100)
    run_load_test(concurrent=20, total_requests=200)

    print("\n✅ 性能测试完成")
