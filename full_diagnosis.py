#!/usr/bin/env python3
"""生成完整诊断报告"""

import sys

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

import json

from core.agents.builtin.config_upgrader import ConfigUpgrader
from tools.real_log_collector import RealLogCollector

print("=" * 70)
print("🔍 ClawsJoy 完整诊断报告")
print("=" * 70)

collector = RealLogCollector()
upgrader = ConfigUpgrader()

# 1. 整体统计
print("\n📊 整体统计:")
print(f"  总升级次数: {len(upgrader.history)}")
print(f"  监控Agent数: 3")
print(
    f"  总交互数: {sum(collector.get_performance_stats(a, 168)['total'] for a in ['chat_agent', 'code_agent', 'vision_agent'])}"
)

# 2. 各Agent详细
for agent in ["chat_agent", "code_agent", "vision_agent"]:
    print(f"\n📊 {agent}:")
    stats = collector.get_performance_stats(agent, 168)
    print(f"  成功率: {stats['success_rate']:.1%}")
    print(f"  总交互: {stats['total']}")
    print(f"  失败: {stats['failures']}")
    if stats.get("failure_types"):
        print(
            f"  主要失败: {max(stats['failure_types'], key=stats['failure_types'].get)}"
        )

# 3. 优化建议
print("\n💡 优化建议:")
print("  1. 超时问题占主导，建议增加 max_tokens")
print("  2. 考虑使用 qwen2.5:3b 处理简单请求")
print("  3. 实现请求缓存减少重复计算")
print("  4. 添加异步处理避免阻塞")

# 4. 保存报告
report = {
    "timestamp": __import__("datetime").datetime.now().isoformat(),
    "total_upgrades": len(upgrader.history),
    "agents": {
        agent: collector.get_performance_stats(agent, 168)
        for agent in ["chat_agent", "code_agent", "vision_agent"]
    },
}

with open("diagnosis_report.json", "w") as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\n📄 详细报告已保存到: diagnosis_report.json")
