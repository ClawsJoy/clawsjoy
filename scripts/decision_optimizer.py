import sys
sys.path.insert(0, "/mnt/d/clawsjoy")
#!/usr/bin/env python3
"""智能决策优化 - 根据历史数据优化决策参数"""
import json
from lib.memory_simple import memory
from datetime import datetime

def analyze_best_params():
    """分析最优参数组合"""
    calibrations = memory.recall_all(category='calibration_log')
    if not calibrations:
        return None
    
    # 提取成功案例的参数
    params = []
    for cal in calibrations:
        if '建议字数' in cal:
            import re
            match = re.search(r'建议字数(\d+)', cal)
            if match:
                params.append(int(match.group(1)))
    
    if params:
        avg_param = sum(params) / len(params)
        return {
            "optimal_word_count": int(avg_param),
            "sample_count": len(params)
        }
    return None

def adjust_decision_threshold():
    """调整决策阈值"""
    outcomes = memory.recall_all(category='workflow_outcome')
    total = len(outcomes)
    success = len([o for o in outcomes if '成功' in o])
    rate = success / total * 100 if total > 0 else 50
    
    # 动态调整阈值
    if rate < 40:
        threshold = 30  # 降低标准
    elif rate < 60:
        threshold = 50
    elif rate < 80:
        threshold = 70
    else:
        threshold = 85
    
    memory.remember(
        f"决策阈值|成功率:{rate:.0f}%|阈值:{threshold}%",
        category="decision_config"
    )
    return threshold

def main():
    best_params = analyze_best_params()
    threshold = adjust_decision_threshold()
    
    if best_params:
        print(f"🎯 最优参数: 字数{best_params['optimal_word_count']} (样本{best_params['sample_count']}个)")
    print(f"⚙️ 决策阈值: {threshold}%")

if __name__ == "__main__":
    main()
