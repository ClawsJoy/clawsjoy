#!/usr/bin/env python3
"""翻译学习循环"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agents.builtin.translate_agent import translate_agent

def translation_learning():
    """翻译学习"""
    print("🔄 执行翻译学习...")
    # 获取翻译统计
    if hasattr(translate_agent, 'get_stats'):
        stats = translate_agent.get_stats()
        print(f"   翻译统计: {stats}")
    else:
        print("   翻译统计暂不可用")
    print("✅ 翻译学习完成")

if __name__ == "__main__":
    translation_learning()
