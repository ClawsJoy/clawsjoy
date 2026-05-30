"""故障学习循环"""

import requests
from datetime import datetime
from core.lib.unified_config import unified_config
from core.lib.smart_config import smart_config


class FaultLearningLoop:
    """故障学习循环"""

    def __init__(self):
        self.learned_faults = []
        self.loop_count = 0
        print("🔧 故障学习循环已启动")

    def detect_faults(self):
        """检测故障"""
        faults = []

        # 检查服务故障
        services = {'gateway': 5002, 'agent': 5005, 'doc': 5008}
        for name, port in services.items():
            try:
                resp = requests.get(unified_config.get_service_url(f"{port}/health"), timeout=3)
                if resp.status_code != 200:
                    faults.append({
                        'type': 'api_error',
                        'service': name,
                        'details': f'HTTP {resp.status_code}',
                        'severity': 'high'
                    })
            except requests.exceptions.ConnectionError:
                faults.append({
                    'type': 'connection_error',
                    'service': name,
                    'details': 'Connection refused',
                    'severity': 'high'
                })
            except Exception as e:
                faults.append({
                    'type': 'unknown_error',
                    'service': name,
                    'details': str(e)[:50],
                    'severity': 'medium'
                })

        return faults

    def learn_fault(self, fault):
        """学习故障模式"""
        self.learned_faults.append({
            'fault': fault,
            'learned_at': datetime.now().isoformat(),
            'count': self.learned_faults.count(fault) + 1
        })
        # 保留最近100条
        if len(self.learned_faults) > 100:
            self.learned_faults = self.learned_faults[-100:]

    def get_statistics(self):
        """获取统计信息"""
        return {
            'total_faults': len(self.learned_faults),
            'unique_faults': len(set(str(f['fault']) for f in self.learned_faults)),
            'loop_count': self.loop_count
        }

    def run_once(self):
        """单次学习循环"""
        self.loop_count += 1
        faults = self.detect_faults()
        for fault in faults:
            self.learn_fault(fault)
        return faults

    def run(self):
        """持续运行"""
        try:
            while True:
                faults = self.run_once()
                if faults:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 发现 {len(faults)} 个故障")
                __import__('time').sleep(30)
        except KeyboardInterrupt:
            print(f"\n学习循环停止，共学习 {len(self.learned_faults)} 个故障")


if __name__ == "__main__":
    loop = FaultLearningLoop()
    loop.run()
