#!/usr/bin/env python3
"""大脑自动训练脚本"""

import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from agent_core.brain_enhanced import brain
from datetime import datetime

print(f"[{datetime.now()}] 开始大脑训练...")

# 获取统计数据
stats = brain.get_stats()
print(f"  经验数: {stats['total_experiences']}")
print(f"  成功率: {stats['success_rate']:.1%}")
print(f"  最佳实践: {stats['best_practices']}")
print(f"  Q表大小: {stats['q_table_size']}")

# 如果有 consolidate 方法则调用
if hasattr(brain, 'consolidate'):
    brain.consolidate()
    print("  记忆巩固完成")

# 保存
if hasattr(brain, '_save'):
    brain._save()
    print("  大脑数据已保存")

print(f"[{datetime.now()}] 训练完成")
