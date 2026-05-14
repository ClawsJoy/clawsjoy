"""智能预测器 - 基于历史数据预测未来状态"""
import json
import time
from pathlib import Path
from datetime import datetime
from collections import deque
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

class IntelligentPredictor:
    def __init__(self):
        self.history = deque(maxlen=100)
        self.predictions_file = Path("data/predictions.json")
        
    def record_metric(self, metric_name, value):
        """记录指标"""
        self.history.append({
            "timestamp": time.time(),
            "metric": metric_name,
            "value": value
        })
        
    def predict_next(self, metric_name, window=5):
        """预测下一个值（简单移动平均 + 趋势）"""
        recent = [h for h in self.history if h["metric"] == metric_name]
        if len(recent) < window:
            return None
            
        values = [h["value"] for h in recent[-window:]]
        avg = sum(values) / len(values)
        
        # 计算趋势
        if len(values) >= 3:
            trend = (values[-1] - values[0]) / len(values)
        else:
            trend = 0
            
        prediction = avg + trend
        
        return {
            "metric": metric_name,
            "predicted_value": round(prediction, 2),
            "trend": "up" if trend > 0 else "down" if trend < 0 else "stable",
            "confidence": min(0.9, len(recent) / 50)
        }
    
    def generate_forecast(self):
        """生成预测报告"""
        from agent_core.brain_enhanced import brain
        stats = brain.get_stats()
        
        # 记录当前指标
        self.record_metric("success_rate", stats.get('success_rate', 0))
        self.record_metric("experience_growth", stats.get('total_experiences', 0))
        
        forecast = {
            "timestamp": datetime.now().isoformat(),
            "predictions": []
        }
        
        # 预测成功率
        success_pred = self.predict_next("success_rate")
        if success_pred:
            forecast["predictions"].append(success_pred)
        
        # 预测经验增长
        exp_pred = self.predict_next("experience_growth")
        if exp_pred:
            forecast["predictions"].append(exp_pred)
        
        # 保存预测
        with open(self.predictions_file, 'w') as f:
            json.dump(forecast, f, indent=2)
        
        return forecast

if __name__ == "__main__":
    predictor = IntelligentPredictor()
    forecast = predictor.generate_forecast()
    print("📈 智能预测报告:")
    print(json.dumps(forecast, indent=2))
