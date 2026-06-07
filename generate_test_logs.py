#!/usr/bin/env python3
"""为所有Agent生成测试日志"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

agents_with_config = [
    "analysis_agent",
    "collaboration_agent",
    "decision_agent",
    "dialect_agent",
    "director_agent",
    "executor_agent",
    "memory_agent",
    "orchestrator",
    "translate_agent",
    "video_agent",
    "video_indexer_agent",
    "writer_agent",
    "youtube_agent",
]


def generate_logs(agent_name, count=20):
    """生成测试日志"""
    logs = []
    for i in range(count):
        # 模拟70%成功率
        success = random.random() > 0.3

        log = {
            "timestamp": (datetime.now() - timedelta(hours=i)).isoformat(),
            "success": success,
            "input": f"测试请求 {i}",
            "output": "测试响应" if success else "",
            "error": None if success else "timeout",
            "agent": agent_name,
        }
        logs.append(log)

    # 保存
    log_file = Path(f"data/conversations/{agent_name}_test.json")
    log_file.parent.mkdir(parents=True, exist_ok=True)

    with open(log_file, "w") as f:
        json.dump({"messages": logs}, f, indent=2)

    print(f"✅ {agent_name}: 生成 {count} 条测试日志")


for agent in agents_with_config:
    generate_logs(agent, 30)

print("\n✅ 已完成！现在可以监控所有Agent了")
