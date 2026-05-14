"""智能核心 V2 - 整合所有智能模块"""
import threading
import time
import json
from datetime import datetime
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

# 导入所有智能模块
from intelligence.analyzer import IntelligenceAnalyzer
from intelligence.predictor import IntelligentPredictor
from intelligence.alerter import IntelligentAlerter
from intelligence.learner import IntelligentLearner
from intelligence.decision_engine import SmartDecisionEngine
from intelligence.task_allocator import SmartTaskAllocator
from intelligence.memory_optimizer import MemoryOptimizer

class SmartCoreV2:
    """智能核心 V2 - 完整版"""
    
    def __init__(self):
        self.analyzer = IntelligenceAnalyzer()
        self.predictor = IntelligentPredictor()
        self.alerter = IntelligentAlerter()
        self.learner = IntelligentLearner()
        self.decision_engine = SmartDecisionEngine()
        self.task_allocator = SmartTaskAllocator()
        self.memory_optimizer = MemoryOptimizer()
        
        self.running = True
        self.cycle_count = 0
        
        print("\n" + "=" * 60)
        print("🧠 ClawsJoy 智能核心 V2 - 完全版")
        print("=" * 60)
        print("模块列表:")
        print("  📊 分析器     - 系统状态分析")
        print("  📈 预测器     - 未来趋势预测")
        print("  🔔 告警器     - 智能阈值告警")
        print("  📚 学习器     - 经验模式学习")
        print("  🧠 决策引擎   - 自主决策")
        print("  🎯 任务分配器 - 智能任务分配")
        print("  💾 记忆优化器 - 记忆健康优化")
        print("=" * 60)
    
    def run_cycle(self):
        """运行一个完整周期"""
        self.cycle_count += 1
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 智能周期 #{self.cycle_count}")
        print("-" * 50)
        
        # 1. 分析
        report = self.analyzer.analyze()
        print(f"📊 健康度: {report['health_score']}/100")
        
        # 2. 预测
        forecast = self.predictor.generate_forecast()
        for pred in forecast.get('predictions', []):
            print(f"📈 预测: {pred['metric']} {pred['trend']} -> {pred['predicted_value']}")
        
        # 3. 记忆优化
        memory_health = self.memory_optimizer.optimize()
        
        # 4. 决策
        if self.cycle_count % 5 == 0:  # 每5周期决策一次
            decision = self.decision_engine.auto_decide()
            print(f"🎯 决策: {decision.get('decision', 'N/A')}")
        
        # 5. 学习
        insights = self.learner.auto_optimize()
        
        return {
            "cycle": self.cycle_count,
            "health_score": report['health_score'],
            "memory_health": memory_health['health_score'],
            "forecast": forecast
        }
    
    def run_loop(self, interval=120):
        """持续运行"""
        print(f"\n🔄 智能循环启动 (间隔: {interval}秒)")
        print("按 Ctrl+C 停止\n")
        
        while self.running:
            try:
                self.run_cycle()
                time.sleep(interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ 错误: {e}")
                time.sleep(10)
    
    def stop(self):
        self.running = False

if __name__ == "__main__":
    core = SmartCoreV2()
    try:
        core.run_loop(interval=120)
    except KeyboardInterrupt:
        core.stop()
        print("\n✅ 智能核心已停止")
