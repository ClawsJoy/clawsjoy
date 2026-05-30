"""真正的故障学习闭环 - 执行真实修复"""

import time
import requests
import subprocess
from datetime import datetime
from core.lib.unified_config import unified_config
from core.lib.smart_config import smart_config


class RealFaultLoop:
    """真正的故障学习闭环 - 执行真实修复"""

    def __init__(self):
        self.fixer = None  # 将在需要时初始化
        self.loop_count = 0

        # 真实服务配置
        self.services = {
            'gateway': {'port': 5002, 'cmd': 'python3 agent_gateway_web.py'},
            'agent': {'port': 5005, 'cmd': 'python3 multi_agent_service_v2.py'},
            'doc': {'port': 5008, 'cmd': 'python3 doc_generator.py'}
        }

        print("\n" + "="*60)
        print("🔧 真实故障检测系统")
        print("="*60)

    def _get_fixer(self):
        """延迟加载修复器"""
        if self.fixer is None:
            from core.intelligence.real_fixer import RealFixer
            self.fixer = RealFixer()
        return self.fixer

    def detect_and_fix(self):
        """检测并修复真实故障"""
        self.loop_count += 1
        fixer = self._get_fixer()

        print(f"\n{'='*50}")
        print(f"🔄 检测周期 #{self.loop_count} - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*50}")

        fixed = []

        # 1. 检查并修复服务
        for name, config in self.services.items():
            try:
                resp = requests.get(unified_config.get_service_url(f"{config['port']}/health"), timeout=3)
                if resp.status_code != 200:
                    print(f"\n❌ {name} 异常 (HTTP {resp.status_code})")
                    if fixer.fix_service(name, config['port'], config['cmd']):
                        fixed.append(name)
            except requests.exceptions.ConnectionError:
                print(f"\n❌ {name} 连接失败")
                if fixer.fix_service(name, config['port'], config['cmd']):
                    fixed.append(name)
            except Exception as e:
                print(f"\n❌ {name} 故障: {str(e)[:50]}")

        # 2. 检查端口冲突
        for port in [5002, 5005, 5008]:
            result = subprocess.run(f"lsof -ti:{port}", shell=True, capture_output=True)
            if result.stdout.strip():
                print(f"\n⚠️ 端口 {port} 冲突")
                fixer.fix_port_conflict(port)

        # 输出结果
        if fixed:
            print(f"\n✅ 本次修复: {fixed}")
        else:
            print(f"\n✅ 无故障")

        return fixed

    def run(self):
        """持续运行"""
        print("\n🚀 启动真实故障监控...")
        print("每30秒检测一次，发现问题立即修复\n")

        try:
            while True:
                self.detect_and_fix()
                print(f"\n⏳ 等待30秒...")
                time.sleep(30)
        except KeyboardInterrupt:
            print("\n\n停止监控")
            print(f"总周期: {self.loop_count}")


if __name__ == "__main__":
    loop = RealFaultLoop()
    loop.run()
