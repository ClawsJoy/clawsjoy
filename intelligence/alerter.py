"""智能告警器 - 基于历史动态调整阈值"""
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

class IntelligentAlerter:
    def __init__(self):
        self.thresholds_file = Path("data/dynamic_thresholds.json")
        self.alert_history = defaultdict(list)
        self.load_thresholds()
        
    def load_thresholds(self):
        """加载动态阈值"""
        if self.thresholds_file.exists():
            with open(self.thresholds_file, 'r') as f:
                self.thresholds = json.load(f)
        else:
            # 初始阈值（会动态调整）
            self.thresholds = {
                "success_rate": {"warning": 0.7, "critical": 0.5, "adaptive": True},
                "response_time": {"warning": 2.0, "critical": 5.0, "adaptive": True},
                "error_count": {"warning": 10, "critical": 50, "adaptive": True}
            }
    
    def save_thresholds(self):
        """保存阈值"""
        with open(self.thresholds_file, 'w') as f:
            json.dump(self.thresholds, f, indent=2)
    
    def adapt_threshold(self, metric_name, recent_values):
        """自适应调整阈值"""
        if not self.thresholds.get(metric_name, {}).get("adaptive", False):
            return
            
        if len(recent_values) < 10:
            return
            
        # 基于历史数据计算动态阈值
        avg = sum(recent_values) / len(recent_values)
        std = (sum((v - avg) ** 2 for v in recent_values) / len(recent_values)) ** 0.5
        
        # 动态阈值 = 平均值 + 2倍标准差
        dynamic_warning = avg + 2 * std
        
        # 更新阈值（平滑变化）
        old_warning = self.thresholds[metric_name]["warning"]
        self.thresholds[metric_name]["warning"] = 0.7 * old_warning + 0.3 * dynamic_warning
        
        print(f"📊 自适应阈值: {metric_name} {old_warning:.2f} -> {self.thresholds[metric_name]['warning']:.2f}")
    
    def check_and_alert(self, metric_name, current_value):
        """检查并告警"""
        if metric_name not in self.thresholds:
            return None
            
        threshold = self.thresholds[metric_name]
        
        if current_value >= threshold.get("critical", float('inf')):
            return {"level": "critical", "message": f"{metric_name} 严重异常: {current_value}"}
        elif current_value >= threshold.get("warning", float('inf')):
            return {"level": "warning", "message": f"{metric_name} 告警: {current_value}"}
        
        return None

if __name__ == "__main__":
    alerter = IntelligentAlerter()
    print("🔔 智能告警器已就绪")
    print(f"动态阈值: {alerter.thresholds}")
