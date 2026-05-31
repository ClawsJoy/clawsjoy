#!/usr/bin/env python3
"""闭环学习定时任务 - 定期运行自学习"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.intelligence.closed_loop import closed_loop
from core.learner.self_learning_coordinator import SelfLearningCoordinator
from core.skills.auto_skill_generator import AutoSkillGenerator

def run_closed_loop():
    print("🔄 运行闭环学习...")
    result = closed_loop.run()
    print(f"   闭环结果: {result.get('status', 'unknown')}")

def run_self_learning():
    print("📚 运行自我学习...")
    coordinator = SelfLearningCoordinator()
    result = coordinator.run_batch([])
    print(f"   学习结果: {result}")

def generate_skills():
    print("⚙️ 自动生成技能...")
    generator = AutoSkillGenerator()
    generated = generator.analyze_and_generate()
    print(f"   生成技能: {generated}")

if __name__ == "__main__":
    run_closed_loop()
    run_self_learning()
    generate_skills()
