"""真实大脑 - 服务健康管理"""

import time
import requests
import subprocess
from datetime import datetime
from core.lib.unified_config import unified_config
from core.lib.smart_config import smart_config


class RealBrain:
    """真实大脑 - 聚焦服务健康管理"""

    def __init__(self):
        self.running = True
        self.stats = {
            'checks': 0,
            'fixes': 0,
            'start_time': datetime.now()
        }
        print("🧠 真实大脑已启动")

    def check_service(self, port, name):
        """检查单个服务"""
        try:
            resp = requests.get(unified_config.get_service_url(f"{port}/health"), timeout=2)
            return resp.status_code == 200
        except Exception:
            return False

    def heal_service(self, name, cmd):
        """修复服务"""
        print(f"🔧 修复 {name}...")
        try:
            subprocess.Popen(cmd, shell=True, cwd=smart_config.ROOT)
            self.stats['fixes'] += 1
            return True
        except Exception as e:
            print(f"   修复失败: {e}")
            return False

    def run_once(self):
        """单次检查和修复"""
        self.stats['checks'] += 1

        services = {
            'gateway': {'port': 5002, 'cmd': 'python3 agent_gateway_web.py'},
            'agent': {'port': 5005, 'cmd': 'python3 multi_agent_service_v2.py'},
        }

        for name, config in services.items():
            if not self.check_service(config['port'], name):
                print(f"⚠ {name} 异常，尝试修复...")
                self.heal_service(name, config['cmd'])
                time.sleep(3)

        return self.stats

    def run(self):
        """持续运行"""
        print("=" * 40)
        print("真实大脑运行中")
        print("=" * 40)

        while self.running:
            self.run_once()
            time.sleep(30)

    def stop(self):
        self.running = False


if __name__ == "__main__":
    brain = RealBrain()
    try:
        brain.run()
    except KeyboardInterrupt:
        brain.stop()
        print("\n大脑停止")
