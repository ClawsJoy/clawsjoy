import sys
sys.path.insert(0, "/mnt/d/clawsjoy")
#!/usr/bin/env python3
"""自动调优 - 根据历史成功率调整参数"""
import json
from lib.memory_simple import memory
from datetime import datetime, timedelta

def analyze_success_rate():
    outcomes = memory.recall_all(category='workflow_outcome')
    total = len(outcomes)
    success = len([o for o in outcomes if '成功' in o])
    rate = success / total * 100 if total > 0 else 0
    return rate, total

def adjust_parameters():
    rate, _ = analyze_success_rate()
    
    adjustments = []
    if rate < 50:
        adjustments.append("建议降低目标时长或放宽质量标准")
    elif rate > 80:
        adjustments.append("当前参数良好，可尝试提高目标")
    
    # 存入记忆
    memory.remember(
        f"auto_tune|成功率:{rate:.0f}%|建议:{','.join(adjustments) if adjustments else '无需调整'}",
        category="auto_tuning"
    )
    return adjustments

if __name__ == "__main__":
    rate, total = analyze_success_rate()
    print(f"当前成功率: {rate:.0f}% ({total}条记录)")
    adjust_parameters()
