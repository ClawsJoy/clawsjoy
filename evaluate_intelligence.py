#!/usr/bin/env python3
"""系统智能化评估脚本"""

import json
import time
from typing import Any, Dict

import requests

BASE_URL = "http://127.0.0.1:5002"


# 先获取 token
def get_token():
    resp = requests.post(
        f"{BASE_URL}/api/user/login", json={"username": "test", "password": "test123"}
    )
    return resp.json().get("token")


TOKEN = get_token()
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

# 测试用例
TEST_CASES = [
    # 1. 意图识别
    {"name": "问候", "message": "你好", "expected": "greeting"},
    {"name": "代码生成", "message": "写一个快速排序", "expected": "code"},
    {"name": "翻译", "message": "翻译 hello 到中文", "expected": "translate"},
    {"name": "分析", "message": "分析Python的优势", "expected": "analysis"},
    # 2. 情感识别
    {
        "name": "开心",
        "message": "今天天气真好，心情特别棒！",
        "expected_emotion": "happy",
    },
    {"name": "沮丧", "message": "我好难过，项目失败了", "expected_emotion": "sad"},
    {"name": "愤怒", "message": "这个结果太让人生气了！", "expected_emotion": "angry"},
    # 3. 长计划编排
    {
        "name": "短视频制作",
        "message": "帮我制作一个关于人工智能的短视频，并写一个脚本",
        "expected_agent": "orchestrator",
    },
    {
        "name": "多步骤任务",
        "message": "先写一个Python脚本，然后生成配图，最后翻译成英文",
        "expected_chain": True,
    },
    # 4. 多轮对话（记忆测试）
    {"name": "多轮1", "message": "我叫小明", "context": True},
    {"name": "多轮2", "message": "我叫什么名字？", "expected_memory": "小明"},
]


def evaluate():
    results = []

    print("=" * 60)
    print("智能化评估报告")
    print("=" * 60)

    for test in TEST_CASES:
        print(f"\n📝 测试: {test['name']}")
        print(f"   消息: {test['message']}")

        start = time.time()
        try:
            resp = requests.post(
                f"{BASE_URL}/api/v5/enhanced/chat",
                headers=HEADERS,
                json={"message": test["message"], "user_id": "eval_user"},
            )
            result = resp.json()
            elapsed = time.time() - start

            print(f"   ✅ 响应: {result.get('response', '')[:100]}...")
            print(f"   ⏱️ 耗时: {elapsed:.2f}s")
            print(f"   🤖 Agent: {result.get('agent', 'unknown')}")
            print(f"   😊 情感: {result.get('detected_emotion', 'unknown')}")

            results.append(
                {
                    "name": test["name"],
                    "success": result.get("success", False),
                    "agent": result.get("agent"),
                    "emotion": result.get("detected_emotion"),
                    "time": elapsed,
                    "full_response": result,
                }
            )

        except Exception as e:
            print(f"   ❌ 失败: {e}")
            results.append({"name": test["name"], "success": False, "error": str(e)})

    # 输出统计
    print("\n" + "=" * 60)
    print("统计结果")
    print("=" * 60)

    success_count = sum(1 for r in results if r.get("success"))
    avg_time = sum(r.get("time", 0) for r in results) / len(results)

    print(
        f"✅ 成功率: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)"
    )
    print(f"⏱️ 平均响应时间: {avg_time:.2f}s")

    # 保存详细报告
    with open("evaluation_report.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n📄 详细报告已保存: evaluation_report.json")


if __name__ == "__main__":
    evaluate()
