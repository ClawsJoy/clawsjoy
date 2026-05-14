"""健康监控器 - 实时监控服务健康状态"""
import time
import requests
import json
from pathlib import Path
from datetime import datetime
from threading import Thread
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

class HealthMonitor:
    def __init__(self):
        self.services = {
            'gateway': {'port': 5002, 'health_url': '/api/health', 'status': 'unknown'},
            'file': {'port': 5003, 'health_url': '/health', 'status': 'unknown'},
            'multi_agent': {'port': 5005, 'health_url': '/health', 'status': 'unknown'},
            'doc_generator': {'port': 5008, 'health_url': '/health', 'status': 'unknown'}
        }
        self.failures = {}
        self.running = True
        self.log_file = Path("logs/monitor.log")
        self.log_file.parent.mkdir(exist_ok=True)
        
    def check_service(self, name, config):
        """检查单个服务"""
        try:
            url = f"http://localhost:{config['port']}{config['health_url']}"
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                return 'healthy'
            else:
                return f'unhealthy (HTTP {resp.status_code})'
        except requests.exceptions.ConnectionError:
            return 'down'
        except Exception as e:
            return f'error: {str(e)[:30]}'
    
    def monitor_loop(self):
        """监控循环"""
        while self.running:
            status_changed = False
            
            for name, config in self.services.items():
                new_status = self.check_service(name, config)
                
                if new_status != config['status']:
                    config['status'] = new_status
                    status_changed = True
                    
                    # 记录状态变化
                    msg = f"{datetime.now().isoformat()} [{name}] {new_status}"
                    print(msg)
                    with open(self.log_file, 'a') as f:
                        f.write(msg + '\n')
                    
                    # 如果是服务down，记录失败
                    if new_status == 'down':
                        if name not in self.failures:
                            self.failures[name] = []
                        self.failures[name].append(datetime.now().isoformat())
            
            time.sleep(10)  # 每10秒检查一次
    
    def get_summary(self):
        """获取摘要"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }
        
        healthy_count = 0
        for name, config in self.services.items():
            summary["services"][name] = config['status']
            if config['status'] == 'healthy':
                healthy_count += 1
        
        summary["healthy_count"] = healthy_count
        summary["total_count"] = len(self.services)
        summary["health_score"] = int(healthy_count / len(self.services) * 100)
        
        return summary
    
    def start(self):
        """启动监控"""
        print("🩺 健康监控器启动")
        print(f"监控服务: {', '.join(self.services.keys())}")
        monitor_thread = Thread(target=self.monitor_loop, daemon=True)
        monitor_thread.start()
        return monitor_thread
    
    def stop(self):
        self.running = False

if __name__ == "__main__":
    monitor = HealthMonitor()
    monitor.start()
    
    try:
        while True:
            time.sleep(30)
            summary = monitor.get_summary()
            print(f"\n📊 健康摘要: {summary['health_score']}%")
    except KeyboardInterrupt:
        monitor.stop()
        print("\n监控已停止")
