"""任务分配器"""

import requests
from collections import defaultdict
from core.lib.unified_config import unified_config
from core.lib.smart_config import smart_config


class SmartTaskAllocator:
    """智能任务分配器"""

    def __init__(self):
        self.agent_performance = defaultdict(list)
        self.task_history = []

    def get_agent_capabilities(self) -> dict:
        """获取所有Agent能力"""
        try:
            resp = requests.get(
                f"http://{smart_config.HOST}:{unified_config.get_port('multi_agent')}/agents",
                timeout=3
            )
            if resp.status_code == 200:
                agents = resp.json().get('agents', [])
                capabilities = {}
                for agent in agents:
                    caps = []
                    if 'Cleaner' in agent:
                        caps.append('cleanup')
                    if 'Engineer' in agent:
                        caps.append('engineering')
                    if 'Security' in agent:
                        caps.append('security')
                    if 'Learning' in agent:
                        caps.append('learning')
                    if 'Supervisor' in agent:
                        caps.append('supervision')
                    if 'Ops' in agent:
                        caps.append('operations')
                    capabilities[agent] = caps if caps else ['general']
                return capabilities
        except Exception:
            pass
        return {}

    def record_performance(self, agent_name: str, task: str, success: bool, duration: float):
        """记录Agent性能"""
        self.agent_performance[agent_name].append({
            'task': task,
            'success': success,
            'duration': duration,
            'timestamp': __import__('time').time()
        })
        # 保留最近100条
        if len(self.agent_performance[agent_name]) > 100:
            self.agent_performance[agent_name] = self.agent_performance[agent_name][-100:]

    def get_best_agent(self, task_type: str) -> str:
        """获取最适合的Agent"""
        best = None
        best_score = -1
        for agent, records in self.agent_performance.items():
            if not records:
                continue
            success_rate = sum(1 for r in records if r['success']) / len(records)
            avg_duration = sum(r['duration'] for r in records) / len(records)
            score = success_rate * 0.7 + (1 / (avg_duration + 1)) * 0.3
            if score > best_score:
                best_score = score
                best = agent
        return best or "orchestrator"


task_allocator = SmartTaskAllocator()
