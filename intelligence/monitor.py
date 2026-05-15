#!/usr/bin/env python3
"""智能监控器 - 使用统一配置"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from lib.unified_config import config
from datetime import datetime
import requests
import time

class SmartMonitor:
    def __init__(self):
        self.log_file = config.get_path('logs') / 'monitor.log'
        self.gateway_port = config.get_port('gateway')
        self.gateway_url = f"http://localhost:{self.gateway_port}"
        self.stats = {"checks": 0, "issues": 0}
    
    def check_service(self, name, url):
        try:
            resp = requests.get(url, timeout=3)
            return resp.status_code == 200
        except:
            return False
    
    def run(self):
        print(f"🔍 智能监控器启动（旁路模式）")
        print(f"   监控网关: {self.gateway_url}")
        print(f"   监控日志: {self.log_file}")
        
        while True:
            self.stats["checks"] += 1
            
            # 监控网关
            api_ok = self.check_service("gateway", f"{self.gateway_url}/api/health")
            if not api_ok:
                self.stats["issues"] += 1
                with open(self.log_file, 'a') as f:
                    f.write(f"{datetime.now()}: API 异常\n")
                print(f"⚠️ {datetime.now().strftime('%H:%M:%S')}: API 异常")
            else:
                # 每10次检查输出一次正常状态
                if self.stats["checks"] % 10 == 0:
                    print(f"✅ {datetime.now().strftime('%H:%M:%S')}: 系统正常 (检查: {self.stats['checks']})")
            
            time.sleep(30)

if __name__ == "__main__":
    monitor = SmartMonitor()
    monitor.run()
