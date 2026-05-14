"""真实大脑 - 服务健康管理"""
import time
import requests
import subprocess
from datetime import datetime
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

# 正确导入大脑模块
from agent_core.brain_enhanced import brain as brain_core

class RealBrain:
    """真实大脑 - 聚焦服务健康管理"""
    
    def __init__(self):
        self.running = True
        self.stats = {
            'checks': 0,
            'fixes': 0,
            'start_time': datetime.now()
        }
        
    def check_service(self, port, name):
        """检查单个服务"""
        try:
            resp = requests.get(f"http://localhost:{port}/health", timeout=2)
            return resp.status_code == 200
        except:
            return False
    
    def heal_service(self, name, cmd):
        """修复服务"""
        print(f"🔧 修复 {name}...")
        subprocess.Popen(cmd, shell=True, cwd="/mnt/d/clawsjoy")
        self.stats['fixes'] += 1
        
        # 记录到大脑核心
        brain_core.record_experience(
            agent="real_brain",
            action=f"heal_{name}",
            result={"success": True},
            context="auto_heal"
        )
    
    def run_once(self):
        """单次检查和修复"""
        self.stats['checks'] += 1
        
        services = {
            'gateway': {'port': 5002, 'cmd': 'python3 agent_gateway_web.py'},
            'agent': {'port': 5005, 'cmd': 'python3 multi_agent_service_v2.py'},
            'doc': {'port': 5008, 'cmd': 'python3 doc_generator.py'}
        }
        
        for name, config in services.items():
            if not self.check_service(config['port'], name):
                print(f"⚠️ {name} 异常，尝试修复...")
                self.heal_service(name, config['cmd'])
                time.sleep(3)
        
        # 显示状态
        brain_stats = brain_core.get_stats()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 检查 #{self.stats['checks']} | 成功率: {brain_stats.get('success_rate', 0)*100:.0f}%")
        
        return self.stats
    
    def run(self):
        """持续运行"""
        print("🧠 真实大脑启动 - 服务健康管理")
        print("=" * 40)
        
        while self.running:
            self.run_once()
            time.sleep(30)
            
    def stop(self):
        self.running = False

if __name__ == "__main__":
    brain_instance = RealBrain()
    try:
        brain_instance.run()
    except KeyboardInterrupt:
        brain_instance.stop()
        print("\n大脑停止")
