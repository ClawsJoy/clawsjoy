#!/usr/bin/env python3
"""分析师报告生成器"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.intelligence.analyst_agent import analyst_agent

if __name__ == "__main__":
    print("📊 生成分析师报告...")
    report = analyst_agent.generate_report()
    print(f"✅ 报告已生成")
