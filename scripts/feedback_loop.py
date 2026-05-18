#!/usr/bin/env python3
"""闭环反馈机制 - 分析结果自动反馈到系统"""

import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
import json
from datetime import datetime
from lib.memory_simple import memory

def process_feedback():
    """处理分析结果并反馈"""
    
    # 获取最新分析结果
    analysis = memory.recall_all(category='enhanced_analysis')
    if not analysis:
        print("无分析结果")
        return
    
    latest = analysis[-1]
    print(f"最新分析: {latest[:100]}...")
    
    # 提取成功率
    import re
    match = re.search(r'成功率:(\d+)%', latest)
    if match:
        rate = int(match.group(1))
        
        # 根据成功率生成反馈
        if rate < 50:
            feedback = f"【系统建议】成功率 {rate}%，低于目标。建议：\n" \
                       "1. 检查失败任务日志\n" \
                       "2. 优化工作流配置\n" \
                       "3. 增加训练样本"
        elif rate < 70:
            feedback = f"【系统建议】成功率 {rate}%，良好但可提升。建议持续优化。"
        else:
            feedback = f"【系统建议】成功率 {rate}%，表现优秀！继续保持。"
        
        # 存储反馈
        memory.remember(
            f"闭环反馈|{datetime.now().isoformat()}|{feedback[:100]}",
            category="system_feedback"
        )
        print(f"✅ 反馈已记录: {feedback[:80]}...")

if __name__ == "__main__":
    process_feedback()
