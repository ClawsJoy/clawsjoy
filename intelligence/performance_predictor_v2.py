"""性能预测器 V2 - 基于历史数据预测系统状态"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

import json
import numpy as np
from datetime import datetime, timedelta
from lib.memory_simple import memory
from lib.skill_loader_v3 import skill_loader

class PerformancePredictorV2:
    """增强版性能预测器"""
    
    def __init__(self):
        self.history_window = 20
        self.prediction_horizon = 5  # 预测未来5个时间点
    
    def get_success_rate_history(self):
        """获取成功率历史"""
        outcomes = memory.recall_all(category='workflow_outcome')
        success_rates = []
        for i, outcome in enumerate(outcomes[-self.history_window:]):
            if '成功' in outcome:
                success_rates.append(100)
            else:
                success_rates.append(0)
        return success_rates
    
    def predict_success_rate(self):
        """预测未来成功率"""
        history = self.get_success_rate_history()
        if len(history) < 5:
            return {"prediction": "数据不足", "confidence": 0.3}
        
        # 简单移动平均预测
        window = min(5, len(history))
        avg = sum(history[-window:]) / window
        trend = history[-1] - history[-2] if len(history) >= 2 else 0
        
        prediction = min(100, max(0, avg + trend * 0.5))
        
        return {
            "prediction": f"{prediction:.1f}%",
            "current_rate": f"{history[-1] if history else 0}%",
            "trend": "上升" if trend > 0 else ("下降" if trend < 0 else "稳定"),
            "confidence": min(0.9, len(history) / 20),
            "next_expected": "成功" if prediction > 70 else ("需关注" if prediction > 50 else "风险")
        }
    
    def predict_resource_usage(self):
        """预测资源使用"""
        # 基于技能数量和服务状态的预测
        skill_count = len(skill_loader.list_skills())
        return {
            "predicted_memory_mb": 500 + skill_count * 2,
            "predicted_cpu_percent": 20 + skill_count * 0.5,
            "status": "正常" if skill_count < 100 else "偏高"
        }
    
    def generate_report(self):
        """生成预测报告"""
        success_pred = self.predict_success_rate()
        resource_pred = self.predict_resource_usage()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "success_rate_prediction": success_pred,
            "resource_prediction": resource_pred,
            "overall_status": "正常" if float(success_pred['prediction'].rstrip('%')) > 60 else "需关注",
            "recommendations": self._get_recommendations(success_pred)
        }
        
        # 存储预测结果
        memory.remember(json.dumps(report), category='performance_predictions')
        
        return report
    
    def _get_recommendations(self, pred):
        """获取建议"""
        rate = float(pred['prediction'].rstrip('%'))
        if rate < 50:
            return ["⚠️ 成功率预测偏低，建议检查系统", "📊 增加测试数据", "🔧 优化技能参数"]
        elif rate < 70:
            return ["📈 持续监控", "🎯 关注关键指标", "🔄 定期校准"]
        else:
            return ["✅ 系统状态良好", "🚀 可继续扩展功能", "📝 记录成功经验"]

predictor = PerformancePredictorV2()

if __name__ == '__main__':
    report = predictor.generate_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))
