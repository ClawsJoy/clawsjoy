"""自适应调优器 V2 - 自动优化系统参数"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

import json
from datetime import datetime
from lib.memory_simple import memory
from lib.skill_loader_v3 import skill_loader

class AdaptiveTunerV2:
    """自适应调优器"""
    
    def __init__(self):
        self.param_history = []
    
    def analyze_performance(self):
        """分析性能瓶颈"""
        outcomes = memory.recall_all(category='workflow_outcome')
        total = len(outcomes)
        success = len([o for o in outcomes if '成功' in o])
        rate = success / total * 100 if total > 0 else 0
        
        errors = memory.recall_all(category='error_knowledge')
        decisions = memory.recall_all(category='executed_decisions')
        
        return {
            "success_rate": rate,
            "error_count": len(errors),
            "decision_count": len(decisions),
            "skill_count": len(skill_loader.list_skills()),
            "bottleneck": "成功率" if rate < 70 else ("错误率" if len(errors) > 20 else "正常")
        }
    
    def suggest_optimization(self):
        """建议优化方案"""
        perf = self.analyze_performance()
        
        suggestions = []
        
        if perf['success_rate'] < 70:
            suggestions.append({
                "target": "success_rate",
                "action": "增加测试数据",
                "priority": "high",
                "expected_improvement": "10-20%"
            })
        
        if perf['error_count'] > 20:
            suggestions.append({
                "target": "error_rate",
                "action": "分析错误模式",
                "priority": "medium",
                "expected_improvement": "30-50%"
            })
        
        if perf['skill_count'] < 50:
            suggestions.append({
                "target": "skill_coverage",
                "action": "扩展技能库",
                "priority": "low",
                "expected_improvement": "功能增强"
            })
        
        return {
            "timestamp": datetime.now().isoformat(),
            "current_performance": perf,
            "suggestions": suggestions,
            "auto_tune_enabled": True
        }
    
    def auto_tune(self):
        """自动调优"""
        analysis = self.suggest_optimization()
        
        # 记录调优建议
        memory.remember(
            json.dumps(analysis, ensure_ascii=False),
            category='auto_tuning'
        )
        
        return analysis

tuner = AdaptiveTunerV2()

if __name__ == '__main__':
    result = tuner.auto_tune()
    print(json.dumps(result, indent=2, ensure_ascii=False))
