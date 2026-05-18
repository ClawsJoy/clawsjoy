#!/usr/bin/env python3
"""智能体练习脚本 - 简化版"""

import sys
import time
import random
import json
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from core.agent.smart_agent import smart_agent
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
    print(f"📚 训练数据: {len(TRAINING_DATA)} 条")
    print(f"🔁 训练轮次: {iterations}")
    print("=" * 60)
    
    success_count = 0
    fail_count = 0
    
    for i in range(iterations):
        user_input = random.choice(TRAINING_DATA)
        
        print(f"\n[{i+1}/{iterations}] 练习: {user_input}")
        
        start_time = time.time()
        result = smart_agent.process(user_input)
        elapsed = time.time() - start_time
        
        if result.get('success'):
            success_count += 1
            status = "✅"
        else:
            fail_count += 1
            status = "❌"
        
        print(f"  {status} {result.get('response', '')[:80]}")
        print(f"  ⏱️ 耗时: {elapsed:.2f}s")
        print(f"  🎯 技能: {result.get('skill')}")
        print(f"  🧠 LLM分析: {result.get('llm_analyzed', False)}")
        
        # 记录学习
        agent_learner.record_interaction(
            user_input=user_input,
            skill=result.get('skill', 'unknown'),
            params=result.get('params', {}),
            success=result.get('success', False),
            response=result.get('response', ''),
            llm_analyzed=result.get('llm_analyzed', False)
        )
        
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("📊 训练统计")
    print("=" * 60)
    print(f"  ✅ 成功: {success_count}")
    print(f"  ❌ 失败: {fail_count}")
    print(f"  📈 成功率: {success_count/(success_count+fail_count)*100:.1f}%")
    print("=" * 60)
    
    # 显示学习报告
    print(agent_learner.get_report())


if __name__ == "__main__":
    train(iterations=20)
