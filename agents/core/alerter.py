"""智能告警系统 - 基于感知的智能告警"""

import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, '/mnt/d/clawsjoy')
from agent_core.perception.multimodal import perception
from agent_core.interaction.environment import environment
from agent_core.brain_enhanced import brain

class SmartAlerter:
    def __init__(self):
        self.alert_history = []
        self.thresholds = {
            "disk_critical": 90,
            "disk_warning": 80,
            "service_retry": 3
        }
    
    def check_and_alert(self):
        """检查并发送告警"""
        anomalies = perception.detect_anomalies()
        
        if not anomalies:
            return {"alerts": []}
        
        alerts = []
        for anomaly in anomalies:
            # 检查是否重复告警
            recent = [a for a in self.alert_history[-10:] if a['message'] == anomaly]
            if len(recent) > self.thresholds['service_retry']:
                continue
            
            alert = {
                "id": f"alert_{datetime.now().timestamp()}",
                "message": anomaly,
                "severity": self._get_severity(anomaly),
                "timestamp": datetime.now().isoformat()
            }
            alerts.append(alert)
            self.alert_history.append(alert)
            
            # 记录到大脑
            brain.record_experience(
                agent="alerter",
                action=f"告警: {anomaly[:50]}",
                result={"success": True, "severity": alert['severity']},
                context="alert"
            )
            
            # 发送通知
            environment.notify_user("admin", anomaly)
        
        return {"alerts": alerts, "count": len(alerts)}
    
    def _get_severity(self, anomaly):
        if "磁盘" in anomaly and "90" in anomaly:
            return "critical"
        if "不可用" in anomaly:
            return "high"
        return "medium"
    
    def get_stats(self):
        return {
            "total_alerts": len(self.alert_history),
            "recent": self.alert_history[-5:] if self.alert_history else []
        }

alerter = SmartAlerter()

if __name__ == '__main__':
    result = alerter.check_and_alert()
    print("告警结果:", result)
