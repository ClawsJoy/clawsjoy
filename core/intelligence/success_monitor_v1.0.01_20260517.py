#!/usr/bin/env python3
"""成功率监控器 v1.0.01 - 配置驱动，从日志读取真实数据"""

import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict

sys.path.insert(0, '/mnt/d/clawsjoy_clean')

from lib.smart_config import smart_config


class SuccessMonitorV1_0_01:
    """成功率监控器 v1.0.01 - 配置驱动"""
    
    VERSION = "1.0.01"
    
    def __init__(self):
        self.root = smart_config.ROOT
        
        # 配置（硬编码默认值，后续可改为配置驱动）
        self.log_path = self.root / "logs" / "active_runner.log"
        self.success_pattern = "✅ 完成"
        self.failure_pattern = "❌ 失败"
        self.window_size = 100
        
    def get_recent_success_rate(self) -> Dict:
        """从日志文件读取真实成功率"""
        if not self.log_path.exists():
            return {"success": 0, "failed": 0, "total": 0, "rate": 0, "source": "no_log"}
        
        content = self.log_path.read_text(encoding='utf-8', errors='ignore')
        lines = content.strip().split('\n')
        
        success = 0
        failed = 0
        
        for line in lines[-self.window_size * 2:]:
            if self.success_pattern in line:
                success += 1
            elif self.failure_pattern in line:
                failed += 1
        
        total = success + failed
        rate = (success / total * 100) if total > 0 else 0
        
        return {
            "success": success,
            "failed": failed,
            "total": total,
            "rate": round(rate, 1),
            "source": "log"
        }
    
    def get_alert_level(self, rate: float) -> str:
        if rate < 30:
            return 'critical'
        elif rate < 50:
            return 'warning'
        else:
            return 'normal'
    
    def check_and_alert(self) -> Dict:
        stats = self.get_recent_success_rate()
        rate = stats['rate']
        level = self.get_alert_level(rate)
        
        alerts = {
            'critical': '🔴 紧急',
            'warning': '🟡 警告',
            'normal': '🟢 正常'
        }
        
        alert_msg = f"{alerts[level]} 成功率: {rate:.1f}% (成功:{stats['success']}, 失败:{stats['failed']}, 来源:{stats.get('source', 'unknown')})"
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {alert_msg}")
        
        return {
            "rate": rate,
            "level": level,
            "alert": alert_msg,
            "stats": stats,
            "version": self.VERSION
        }
    
    def get_status(self) -> Dict:
        return {
            "monitor_version": self.VERSION,
            "log_path": str(self.log_path),
            "window_size": self.window_size,
            "last_check": datetime.now().isoformat()
        }


if __name__ == "__main__":
    monitor = SuccessMonitorV1_0_01()
    result = monitor.check_and_alert()
    print(f"\n📊 详细统计: {result['stats']}")
    print(f"📌 监控器版本: {monitor.VERSION}")
