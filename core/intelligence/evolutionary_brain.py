"""进化大脑 - 自主决策和进化"""

import time
import requests
from datetime import datetime
from core.lib.unified_config import unified_config
from core.lib.smart_config import smart_config


class EvolutionaryBrain:
    """进化大脑"""

    def __init__(self):
        self.running = True
        self.evolution_count = 0
        self.decisions = []
        print("🧠 进化大脑已启动")

    def _check_service(self, port):
        """检查服务"""
        try:
            resp = requests.get(unified_config.get_service_url(f"{port}/health"), timeout=2)
            return resp.status_code == 200
        except Exception:
            return False

    def decision_loop(self):
        """决策模块 - 自主决策"""
        while self.running:
            # 检查核心服务
            services_healthy = True
            for port in [5002, 5005, 5008]:
                if not self._check_service(port):
                    services_healthy = False
                    break

            # 做出决策
            decision = {
                'timestamp': datetime.now().isoformat(),
                'action': 'maintain' if services_healthy else 'repair',
                'services_healthy': services_healthy
            }
            self.decisions.append(decision)

            # 保留最近100条决策
            if len(self.decisions) > 100:
                self.decisions = self.decisions[-100:]

            time.sleep(30)

    def evolve(self):
        """进化"""
        self.evolution_count += 1
        return {'evolved': True, 'count': self.evolution_count}

    def get_stats(self):
        """获取统计信息"""
        return {
            'evolution_count': self.evolution_count,
            'decisions_count': len(self.decisions),
            'running': self.running
        }

    def start(self):
        """启动大脑"""
        self.running = True
        import threading
        thread = threading.Thread(target=self.decision_loop, daemon=True)
        thread.start()
        return {'status': 'started'}

    def stop(self):
        """停止大脑"""
        self.running = False
        return {'status': 'stopped'}


evolutionary_brain = EvolutionaryBrain()
