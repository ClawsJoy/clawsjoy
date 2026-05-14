"""自愈执行器 - 自动恢复失败的服务"""
import subprocess
import time
import requests
from pathlib import Path
from datetime import datetime
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

class SelfHealer:
    def __init__(self):
        self.services = {
            'gateway': {
                'port': 5002,
                'cmd': 'python3 agent_gateway_web.py',
                'health_url': '/api/health',
                'restart_count': 0,
                'last_restart': None
            },
            'multi_agent': {
                'port': 5005,
                'cmd': 'python3 multi_agent_service_v2.py',
                'health_url': '/health',
                'restart_count': 0,
                'last_restart': None
            },
            'doc_generator': {
                'port': 5008,
                'cmd': 'python3 doc_generator.py',
                'health_url': '/health',
                'restart_count': 0,
                'last_restart': None
            }
        }
        self.heal_log = Path("logs/heal.log")
        self.heal_log.parent.mkdir(exist_ok=True)
        
    def is_healthy(self, service_name, config):
        """检查服务健康"""
        try:
            url = f"http://localhost:{config['port']}{config['health_url']}"
            resp = requests.get(url, timeout=3)
            return resp.status_code == 200
        except:
            return False
    
    def restart_service(self, service_name, config):
        """重启服务"""
        from datetime import datetime
        
        print(f"🔄 重启 {service_name}...")
        
        # 杀死进程
        cmd_parts = config['cmd'].split()
        process_name = cmd_parts[-1] if len(cmd_parts) > 1 else cmd_parts[0]
        subprocess.run(f"pkill -f '{process_name}'", shell=True, capture_output=True)
        time.sleep(2)
        
        # 启动服务
        subprocess.Popen(config['cmd'], shell=True, cwd='/mnt/d/clawsjoy')
        time.sleep(3)
        
        # 记录重启
        config['restart_count'] += 1
        config['last_restart'] = datetime.now().isoformat()
        
        msg = f"{datetime.now().isoformat()} [{service_name}] 重启 #{config['restart_count']}"
        print(f"   ✅ {msg}")
        
        with open(self.heal_log, 'a') as f:
            f.write(msg + '\n')
    
    def heal_loop(self):
        """自愈循环"""
        print("🩺 自愈执行器启动")
        
        while True:
            for name, config in self.services.items():
                if not self.is_healthy(name, config):
                    print(f"⚠️ {name} 不健康，尝试恢复...")
                    self.restart_service(name, config)
            
            time.sleep(30)  # 每30秒检查一次
    
    def get_stats(self):
        """获取自愈统计"""
        stats = {}
        for name, config in self.services.items():
            stats[name] = {
                'restart_count': config['restart_count'],
                'last_restart': config['last_restart']
            }
        return stats

if __name__ == "__main__":
    healer = SelfHealer()
    try:
        healer.heal_loop()
    except KeyboardInterrupt:
        print("\n自愈执行器已停止")
