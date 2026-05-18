#!/usr/bin/env python3
"""验证智能化模块"""

import sys
sys.path.insert(0, '/mnt/d/clawsjoy_clean')

print("=" * 60)
print("ClawsJoy 智能化模块验证")
print("=" * 60)

# 1. 成功率预测器
print("\n1. 成功率预测器:")
from lib.success_predictor import success_predictor
stats = success_predictor.get_stats()
print(f"   版本: {stats['version']}")
print(f"   跟踪任务: {stats['total_tasks_tracked']}")

best = success_predictor.get_best_tasks(3)
print(f"\n   高成功率任务:")
for task in best:
    print(f"     ✅ {task['task']}: {task['rate']*100:.0f}% ({task['samples']}次)")

# 2. 智能调度器
print("\n2. 智能调度器:")
from lib.smart_scheduler import smart_scheduler
sched_stats = smart_scheduler.get_schedule_stats()
print(f"   版本: {sched_stats['version']}")
print(f"   启用: {sched_stats['enabled']}")

# 3. 动态阈值
print("\n3. 动态阈值调整器:")
from lib.dynamic_threshold import dynamic_threshold
thresh_stats = dynamic_threshold.get_stats()
print(f"   版本: {thresh_stats['version']}")
print(f"   质量阈值: {thresh_stats['current']['quality_min_score']}")
print(f"   重试阈值: {thresh_stats['current']['max_retry_same_error']}")

# 4. API 测试
print("\n4. API 接口测试:")
import urllib.request
import json

try:
    resp = urllib.request.urlopen('http://localhost:5011/api/intelligence/stats', timeout=3)
    data = json.loads(resp.read().decode())
    print(f"   ✅ API 正常: predictor 版本 {data['predictor']['version']}")
except Exception as e:
    print(f"   ⚠️ API 未就绪: {e}")

print("\n" + "=" * 60)
print("✅ 智能化模块验证完成")
print("=" * 60)

if __name__ == "__main__":
    pass
