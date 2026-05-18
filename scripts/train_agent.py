#!/usr/bin/env python3
"""智能体练习脚本 - 让智能体通过练习成长"""

import sys
import time
import random
sys.path.insert(0, 'core')

from agent.learning_agent import learning_agent
from core.agent.learner import agent_learner

# 练习数据集
TRAINING_DATA = [
    "生成一个中年男人的形象",
    "画一只可爱的猫咪",
    "创建一张风景图片",
    "生成一个20岁年轻女孩的形象",
    "画一个卡通人物",
    "帮我生成一张晚霞的图片",
    "每天上午9点提醒我开会",
    "每天晚上10点提醒我睡觉",
    "每周一早上提醒我写周报",
    "生成一个科幻风格的机器人",
    "画一幅山水画",
    "创建一个古代侠客的形象"
]


def train(iterations: int = 10):
    """训练智能体"""
    print("=" * 60)
    print("🤖 智能体训练开始")
    print("=" * 60)
    
    for i in range(iterations):
        # 随机选择训练数据
        user_input = random.choice(TRAINING_DATA)
        
        print(f"\n[{i+1}/{iterations}] 练习: {user_input}")
        
        start_time = time.time()
        result = learning_agent.process(user_input)
        elapsed = time.time() - start_time
        
        status = "✅" if result.get('success') else "❌"
        print(f"  {status} {result.get('response', '')[:80]}")
        print(f"  ⏱️ 耗时: {elapsed:.2f}s")
        
        # 短暂休息，避免过载
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("训练完成！")
    print(agent_learner.get_report())
    print("=" * 60)


if __name__ == "__main__":
    train(iterations=20)
