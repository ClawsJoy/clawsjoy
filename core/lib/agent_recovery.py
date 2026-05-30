from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

"""Agent 自动恢复机制"""

import subprocess
import time
from datetime import datetime
from core.lib.agent_health import agent_health
from core.lib.agent_registry import agent_registry

class AgentRecovery:
    """Agent 自动恢复"""
    
    def __init__(self):
        self.recovery_log = []
    
    def recover_agent(self, agent_id):
        """恢复单个 Agent"""
        health = agent_health.check_agent(agent_id)
        if health.get('status') == 'healthy':
            return {"success": True, "message": "Agent 已健康"}

        # 恢复策略
        if agent_id == 'orchestrator':
            # 重启网关
            subprocess.run(['pkill', '-f', 'agent_gateway_web'])
            time.sleep(2)
            subprocess.Popen(['python3', 'agent_gateway_web.py'])
            result = {"action": "restart_gateway", "success": True}
        else:
            # 其他 Agent 的恢复逻辑
            result = {"action": "skip", "success": False}

        self.recovery_log.append({
            "agent": agent_id,
            "timestamp": datetime.now().isoformat(),
            "action": result.get('action'),
            "success": result.get('success')
        })

        return result
    
    def recover_all(self):
        """恢复所有不健康的 Agent"""
        health = agent_health.get_summary()
        results = {}

        for agent_id in health.get('details', {}):
            if health['details'][agent_id].get('status') != 'healthy':
                results[agent_id] = self.recover_agent(agent_id)

        return results
    
    def get_recovery_log(self, limit=10):
        """获取恢复日志"""
        return self.recovery_log[-limit:]

agent_recovery = AgentRecovery()
