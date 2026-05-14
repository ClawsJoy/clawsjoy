"""性能预测器 - 预测系统未来状态"""

import json
import numpy as np
from collections import deque
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.brain_enhanced import brain

class PerformancePredictor:
    def __init__(self, window_size=20):
        self.window_size = window_size
        self.history = deque(maxlen=window_size)
        self.predictions = []
        self.prediction_file = Path("data/predictions.json")
        self._load_history()
    
    def _load_history(self):
        if self.prediction_file.exists():
            with open(self.prediction_file, 'r') as f:
                data = json.load(f)
                self.history = deque(data.get('history', []), maxlen=self.window_size)
                self.predictions = data.get('predictions', [])
    
    def _save_history(self):
        with open(self.prediction_file, 'w') as f:
            json.dump({
                'history': list(self.history),
                'predictions': self.predictions[-50:]
            }, f, indent=2)
    
    def add_data_point(self, data):
        """添加数据点"""
        self.history.append(data)
        self._save_history()
    
    def get_current_metrics(self):
        """获取当前指标"""
        stats = brain.get_stats()
        import subprocess
        result = subprocess.run("df -h / | tail -1 | awk '{print $5}'", 
                                shell=True, capture_output=True, text=True)
        disk = result.stdout.strip().replace('%', '')
        
        return {
            "timestamp": datetime.now().isoformat(),
            "success_rate": stats.get('success_rate', 0),
            "total_experiences": stats.get('total_experiences', 0),
            "disk_usage": int(disk) if disk.isdigit() else 0,
            "knowledge_size": stats.get('knowledge_graph_nodes', 0)
        }
    
    def predict_next(self):
        """预测下一个时间点的值"""
        if len(self.history) < 5:
            return {"error": "数据不足，需要更多历史数据"}
        
        # 简单移动平均预测
        recent = list(self.history)[-5:]
        
        predictions = {
            "success_rate": np.mean([h['success_rate'] for h in recent]),
            "disk_usage": np.mean([h['disk_usage'] for h in recent]) + 1,  # 趋势向上
            "knowledge_size": np.mean([h['knowledge_size'] for h in recent]) + 0.5
        }
        
        # 添加趋势修正
        if len(self.history) >= 10:
            older = list(self.history)[-10:-5]
            trend_success = np.mean([h['success_rate'] for h in recent]) - np.mean([h['success_rate'] for h in older])
            predictions["success_rate"] += trend_success * 0.3
        
        predictions["success_rate"] = min(1.0, max(0, predictions["success_rate"]))
        
        return predictions
    
    def predict_future(self, steps=5):
        """预测未来多个时间点"""
        predictions = []
        current = self.get_current_metrics()
        
        for i in range(steps):
            # 简单线性外推
            pred = {
                "step": i + 1,
                "success_rate": min(1.0, current['success_rate'] + 0.01 * i),
                "disk_usage": current['disk_usage'] + i * 0.5,
                "knowledge_size": current['knowledge_size'] + i * 0.3
            }
            predictions.append(pred)
        
        return predictions
    
    def alert_if_needed(self, predictions):
        """根据预测结果告警"""
        alerts = []
        prediction = {}
        
        if predictions['disk_usage'] > 85:
            alerts.append(f"预测 {predictions['disk_usage']:.0f}% 磁盘使用率，建议清理")
        
        if predictions['success_rate'] < 0.6:
            alerts.append(f"预测成功率 {predictions['success_rate']:.0%}，可能下降")
        
        return alerts
    
    def run_prediction_cycle(self):
        """运行一次预测周期"""
        print("\n" + "="*50)
        print("🔮 性能预测")
        print("="*50)
        
        # 添加当前数据
        current = self.get_current_metrics()
        self.add_data_point(current)
        print(f"📊 当前: 成功率={current['success_rate']:.1%}, 磁盘={current['disk_usage']}%")
        
        # 预测
        prediction = self.predict_next()
        if 'error' not in prediction:
            print(f"🔮 预测: 成功率={prediction['success_rate']:.1%}, 磁盘={prediction['disk_usage']:.0f}%")
            
            # 检查告警
            alerts = self.alert_if_needed(prediction)
            for alert in alerts:
                print(f"⚠️ {alert}")
            
            # 记录
            self.predictions.append({
                "timestamp": datetime.now().isoformat(),
                "current": current,
                "prediction": prediction,
                "alerts": alerts
            })
            self._save_history()
        
        alerts = []
        return {"current": current, "prediction": prediction, "alerts": alerts}

predictor = PerformancePredictor()

if __name__ == '__main__':
    predictor.run_prediction_cycle()
