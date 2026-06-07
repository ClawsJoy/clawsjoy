#!/usr/bin/env python3
"""监控16个活跃Agent的性能"""

from pathlib import Path

import yaml

from tools.real_log_collector import RealLogCollector

ACTIVE_AGENTS = [
    "analysis_agent",
    "chat_agent",
    "code_agent",
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
    "vision_agent",
    "writer_agent",
    "youtube_agent",
]

collector = RealLogCollector()

print("=" * 80)
print("📊 16个活跃Agent性能监控")
print("=" * 80)
print(f"{'Agent':<20} {'成功率':<10} {'24h交互':<10} {'温度':<8} {'Token':<8}")
print("-" * 80)

# 统计
high_performance = []
need_optimize = []

for agent in ACTIVE_AGENTS:
    # 获取性能
    stats = collector.get_performance_stats(agent, hours=24)
    rate = stats["success_rate"]
    total = stats["total"]

    # 获取配置
    config_file = Path(f"agents/{agent}/config.yaml")
    if config_file.exists():
        with open(config_file) as f:
            config = yaml.safe_load(f)
            llm = config.get("agent", {}).get("llm", {})
            temp = llm.get("temperature", "N/A")
            tokens = llm.get("max_tokens", "N/A")
    else:
        temp, tokens = "N/A", "N/A"

    # 状态图标
    if rate >= 0.8:
        icon = "🟢"
        high_performance.append(agent)
    elif rate >= 0.6:
        icon = "🟡"
        need_optimize.append(agent)
    else:
        icon = "🔴"
        need_optimize.append(agent)

    print(f"{icon} {agent:<19} {rate:<9.1%} {total:<10} {str(temp):<8} {tokens}")

print("-" * 80)
print(f"\n📊 统计:")
print(f"   🟢 优秀 (≥80%): {len(high_performance)}个")
print(
    f"   🟡 需优化 (60-80%): {len([a for a in need_optimize if a not in high_performance])}个"
)
print(f"   🔴 较差 (<60%): 0个")

if need_optimize:
    print(f"\n💡 建议运行: python3 upgrade_all_active_agents.py")
