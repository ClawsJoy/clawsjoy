#!/usr/bin/env python3
"""扫描所有Agent的当前配置和状态"""

from pathlib import Path

import yaml

from tools.real_log_collector import RealLogCollector

# 所有Agent列表
agents = [
    "analysis_agent",
    "calculator_agent",
    "chat_agent",
    "code_agent",
    "collaboration_agent",
    "decision_agent",
    "dialect_agent",
    "director_agent",
    "executor_agent",
    "file_agent",
    "memory_agent",
    "orchestrator",
    "proactive_agent",
    "translate_agent",
    "video_agent",
    "video_indexer_agent",
    "vision_agent",
    "writer_agent",
    "youtube_agent",
]

collector = RealLogCollector()

print("=" * 80)
print("📊 ClawsJoy 全Agent状态扫描")
print("=" * 80)
print(f"{'Agent':<20} {'模型':<15} {'温度':<6} {'Token':<8} {'日志':<8} {'状态'}")
print("-" * 80)

agent_status = []

for agent in agents:
    config_file = Path(f"agents/{agent}/config.yaml")

    if not config_file.exists():
        print(f"{agent:<20} {'无配置':<15} {'-':<6} {'-':<8} {'-':<8} ⚠️ 缺失")
        continue

    # 读取配置
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)

    llm = config.get("agent", {}).get("llm", {})
    model = llm.get("model", "N/A")[:15]
    temp = llm.get("temperature", "N/A")
    tokens = llm.get("max_tokens", "N/A")

    # 检查是否有日志
    logs = collector.collect_agent_logs(agent, hours=168)
    log_count = len(logs)

    # 状态判断
    if log_count > 0:
        status = "✅ 活跃"
    else:
        status = "💤 无数据"

    print(
        f"{agent:<20} {model:<15} {str(temp):<6} {str(tokens):<8} {log_count:<8} {status}"
    )
    agent_status.append(
        {
            "name": agent,
            "model": model,
            "temp": temp,
            "tokens": tokens,
            "logs": log_count,
        }
    )

print("-" * 80)
active = sum(1 for a in agent_status if a["logs"] > 0)
print(
    f"📊 总计: {len(agents)} 个Agent, 活跃: {active} 个, 待配置: {len(agents)-active} 个"
)
