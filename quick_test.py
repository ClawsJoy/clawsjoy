import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests

BASE = "http://127.0.0.1:5002"


def test_one():
    start = time.time()
    try:
        r = requests.post(
            f"{BASE}/api/v5/enhanced/chat",
            json={"user_id": "test", "message": "你好"},
            timeout=30,
        )
        return time.time() - start, r.status_code == 200
    except Exception as e:
        return time.time() - start, False


print("🚀 快速性能测试")
print("=" * 40)

# 单次
dur, ok = test_one()
print(f"单次请求: {dur*1000:.0f}ms, {'✅' if ok else '❌'}")

# 5并发
with ThreadPoolExecutor(max_workers=5) as ex:
    futures = [ex.submit(test_one) for _ in range(10)]
    times = [f.result()[0] for f in futures]
    avg = sum(times) / len(times)
    print(f"10请求(5并发): 平均 {avg*1000:.0f}ms")

print("\n✅ 测试完成")
