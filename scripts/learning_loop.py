#!/usr/bin/env python3
"""学习反馈循环 - 自动分析失败并学习"""

import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
import json
from datetime import datetime
from lib.memory_simple import memory
from agent_core.brain_enhanced import brain

def analyze_failures():
    """分析失败记录并学习"""
    outcomes = memory.recall_all(category='workflow_outcome')
    failures = [o for o in outcomes if '失败' in o]
    
    print(f"📊 分析 {len(failures)} 条失败记录")
    
    # 提取失败模式
    failure_patterns = {}
    for f in failures:
        # 提取关键词
        if '视频' in f:
            pattern = 'video_failure'
        elif '图像' in f or '图片' in f:
            pattern = 'image_failure'
        elif 'API' in f or '网关' in f:
            pattern = 'api_failure'
        elif '记忆' in f or '向量' in f:
            pattern = 'memory_failure'
        else:
            pattern = 'other_failure'
        
        failure_patterns[pattern] = failure_patterns.get(pattern, 0) + 1
    
    print("\n失败模式统计:")
    for pattern, count in failure_patterns.items():
        print(f"  {pattern}: {count} 次")
    
    # 为高频失败添加学习经验
    if failure_patterns.get('video_failure', 0) > 3:
        brain.record_experience(
            agent="learning_loop",
            action="视频失败频繁，检查素材和配置",
            result={"success": True},
            context="视频制作失败率较高，建议优化工作流"
        )
        print("✅ 已学习: 视频失败处理")
    
    return failure_patterns

if __name__ == "__main__":
    print("=" * 50)
    print(f"学习反馈循环 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    analyze_failures()
    
    # 显示大脑状态
    stats = brain.get_stats()
    print(f"\n🧠 大脑状态:")
    print(f"   总经验: {stats.get('total_experiences', 0)}")
    print(f"   成功率: {stats.get('success_rate', 0):.1f}%")
