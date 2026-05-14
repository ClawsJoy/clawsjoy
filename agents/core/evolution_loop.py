#!/usr/bin/env python3
"""完整进化循环 - 整合所有智能模块"""

import time
import sys
from datetime import datetime

sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain
from agents.core.metacognition import metacog
from agents.core.self_improver import self_improver
from agents.core.autonomous_decider import autonomous_decider
from agents.core.reflection_engine import reflection_engine
from agents.core.active_explorer import active_explorer
from agents.core.adaptive_tuner import tuner
from agents.core.performance_predictor import predictor
from agents.core.smart_scheduler import scheduler
from agents.core.resource_optimizer import optimizer
from agent_core.perception.multimodal import perception
from agent_core.interaction.environment import environment

class EvolutionLoop:
    def __init__(self):
        self.cycle = 0
    
    def run_cycle(self):
        self.cycle += 1
        print(f"\n{'='*60}")
        print(f"🧬 进化周期 #{self.cycle} - {datetime.now().isoformat()}")
        print(f"{'='*60}")
        
        # 1. 感知
        stats = brain.get_stats()
        print(f"📊 状态: 经验={stats['total_experiences']}, 成功率={stats['success_rate']:.1%}")
        
        # 2. 元认知分析
        print("\n🧠 元认知...")
        analysis = metacog.analyze_learning_effectiveness()
        strategy = metacog.adjust_strategy()
        
        # 3. 自主决策
        print("\n🎯 自主决策...")
        decision_result = autonomous_decider.run_cycle()
        
        # 4. 多模态感知
        print("\n👁️ 多模态感知...")
        system_state = perception.perceive_all()
        
        # 5. 反思（每3周期）
        if self.cycle % 3 == 0:
            print("\n💭 深度反思...")
            reflection_engine.reflect()
        
        # 6. 探索（每2周期）
        if self.cycle % 2 == 0:
            print("\n🔬 主动探索...")
            active_explorer.explore(rounds=1)
        
        # 7. 自我改进（每4周期）
        if self.cycle % 4 == 0:
            print("\n🔧 自我改进...")
            self_improver.improve()
        
        # 8. 自适应调优（每10周期）
        if self.cycle % 10 == 0:
            print("\n🎛️ 自适应调优...")
            tuner.tune()
        
        # 9. 性能预测（每5周期）
        if self.cycle % 5 == 0:
            print("\n🔮 性能预测...")
            predictor.run_prediction_cycle()
        
        # 10. 资源优化（每3周期）
        if self.cycle % 3 == 0:
            print("\n⚡ 资源优化...")
            optimizer.optimize()
        
        # 11. 记录周期
        brain.record_experience(
            agent="evolution_loop",
            action=f"进化周期 #{self.cycle}",
            result={"success": True, "strategy": strategy.get('strategy')},
            context=f"成功率={stats['success_rate']:.1%}"
        )
        
        # 12. 调度统计
        print(f"\n📋 调度统计: {scheduler.get_stats()}")
        
        return {"cycle": self.cycle, "stats": stats}

if __name__ == '__main__':
    loop = EvolutionLoop()
    loop.run_cycle()
    print("\n✅ 进化完成")
