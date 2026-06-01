#!/usr/bin/env python3
"""持续训练脚本 - 定期更新模型"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

def train():
    print("=" * 50)
    print("ClawsJoy 持续训练")
    print("=" * 50)
    
    from engine.synthetic import synthetic_generator
    from engine.active_learning import active_learning_engine
    from engine.rl import rl_engine
    from engine.transfer import transfer_engine
    from engine.meta import meta_engine
    
    # 1. 生成新合成数据
    print("\n1️⃣ 生成新合成数据...")
    new_data = synthetic_generator.generate_all(samples_per_intent=10)
    print(f"   ✅ 生成 {sum(len(v) for v in new_data.values())} 条")
    
    # 2. 处理待标注请求
    print("\n2️⃣ 处理待标注请求...")
    pending = active_learning_engine.get_pending_requests()
    print(f"   📋 待处理: {len(pending)} 条")
    
    # 3. 更新强化学习
    print("\n3️⃣ 更新强化学习策略...")
    try:
        # 初始化一些基础状态
        base_states = ['code_intent', 'weather_intent', 'translate_intent']
        base_actions = ['code_agent', 'weather_skill', 'translate_agent']
        for state, action in zip(base_states, base_actions):
            rl_engine.update(state, action, 0.8, "completed", base_actions)
    except Exception as e:
        print(f"   ⚠️ 强化学习更新: {e}")
    stats = rl_engine.get_stats()
    print(f"   📊 Q表大小: {stats['q_table_size']}")
    
    # 4. 迁移学习
    print("\n4️⃣ 执行迁移学习...")
    try:
        result = transfer_engine.transfer("python", "code", {"pattern": "recursive"})
        print(f"   🔄 迁移结果: {result.get('transferred_count', 0)} 项")
    except Exception as e:
        print(f"   ⚠️ 迁移学习: {e}")
    
    # 5. 元学习优化
    print("\n5️⃣ 元学习策略优化...")
    best = meta_engine.get_best_strategy("code")
    print(f"   🎯 最佳策略: {best}")
    
    print("\n✅ 训练完成!")
    print(f"   时间: {datetime.now().isoformat()}")

if __name__ == "__main__":
    train()
