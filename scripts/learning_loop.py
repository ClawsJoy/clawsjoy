#!/usr/bin/env python3
"""学习循环 - 使用完整学习框架"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agents.builtin.learning_agent import learning_agent

if __name__ == "__main__":
    print("🔄 执行学习循环...")
    learning_agent.run_learning_cycle()
