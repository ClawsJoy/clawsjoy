#!/usr/bin/env python3
"""成功率监控 - 实时监控并预警"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

import time
from lib.memory_simple import memory
from datetime import datetime

class SuccessMonitor:
    def __init__(self):
        self.window_size = 20  # 最近20次任务
    
    def get_recent_success_rate(self):
        outcomes = memory.recall_all(category='workflow_outcome')[-self.window_size:]
        if not outcomes:
            return 0
        success = len([o for o in outcomes if '成功' in o])
        return success / len(outcomes) * 100
    
    def check_and_alert(self):
        rate = self.get_recent_success_rate()
        
        if rate < 30:
            alert = f"🔴 紧急: 成功率仅{rate:.0f}%，需要立即干预"
            level = "critical"
        elif rate < 50:
            alert = f"🟡 警告: 成功率{rate:.0f}%，低于目标"
            level = "warning"
        else:
            alert = f"🟢 正常: 成功率{rate:.0f}%"
            level = "normal"
        
        # 记录到记忆
        memory.remember(
            f"成功率监控|{rate:.0f}%|等级:{level}|时间:{datetime.now().isoformat()}",
            category="success_monitoring"
        )
        
        if level != "normal":
            print(f"{datetime.now().strftime('%H:%M:%S')} {alert}")
        
        return {"rate": rate, "level": level, "alert": alert}

if __name__ == "__main__":
    monitor = SuccessMonitor()
    monitor.check_and_alert()
