"""智能核心 - 统一入口，整合所有智能模块"""
import threading
import time
import json
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from intelligence.analyzer import IntelligenceAnalyzer
from intelligence.predictor import IntelligentPredictor
from intelligence.alerter import IntelligentAlerter
from intelligence.learner import IntelligentLearner
from agent_core.brain_enhanced import brain

class SmartCore:
    """智能核心 - 整合所有智能能力"""
    
    def __init__(self):
        self.analyzer = IntelligenceAnalyzer()
        self.predictor = IntelligentPredictor()
        self.alerter = IntelligentAlerter()
        self.learner = IntelligentLearner()
        self.running = True
        
        print("🧠 智能核心启动")
        print("=" * 50)
        print("   📊 分析器 - 系统状态分析")
        print("   📈 预测器 - 未来趋势预测")
        print("   🔔 告警器 - 智能阈值告警")
        print("   📚 学习器 - 经验模式学习")
        print("=" * 50)
    
    def run_once(self):
        """执行一次完整智能分析"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 智能分析循环")
        print("-" * 40)
        
        # 1. 分析
        report = self.analyzer.analyze()
        print(f"📊 健康度: {report['health_score']}/100")
        
        # 2. 预测
        forecast = self.predictor.generate_forecast()
        for pred in forecast.get('predictions', []):
            print(f"📈 预测: {pred['metric']} -> {pred['predicted_value']} ({pred['trend']})")
        
        # 3. 学习
        insights = self.learner.auto_optimize()
        
        # 4. 获取大脑统计
        stats = brain.get_stats()
        
        return {
            "health_score": report['health_score'],
            "forecast": forecast,
            "insights": insights,
            "stats": stats
        }
    
    def run_loop(self, interval=60):
        """持续运行智能循环"""
        print(f"\n🔄 智能循环启动 (间隔: {interval}秒)")
        
        while self.running:
            try:
                self.run_once()
                time.sleep(interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ 智能循环错误: {e}")
                time.sleep(10)
    
    def stop(self):
        self.running = False

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        # 单次运行
        core = SmartCore()
        result = core.run_once()
        print("\n✅ 完成")
    else:
        # 持续运行
        core = SmartCore()
        try:
            core.run_loop(interval=60)
        except KeyboardInterrupt:
            core.stop()
            print("\n✅ 智能核心已停止")
