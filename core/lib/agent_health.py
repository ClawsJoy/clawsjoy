from lib.smart_config import smart_config
"""Agent 健康检查模块"""

import subprocess
import requests
from datetime import datetime
from lib.agent_registry import agent_registry
from lib.service_registry import service_registry

class AgentHealthCheck:
    """Agent 健康检查"""
    
    def __init__(self):
        self.health_history = {}
    
    def check_agent(self, agent_id):
        """检查单个 Agent 健康状态"""
        agent = agent_registry.get(agent_id)
        if not agent:
            return {"status": "unknown", "error": "Agent 不存在"}
        
        # 检查 HTTP 端点
        if agent.get('endpoint', {}).get('port'):
            port = agent['endpoint']['port']
            health_path = agent.get('health_check', {}).get('path', '/health')
            try:
                resp = requests.get(ff"{smart_config.get_service_url("{port}{health_path}", timeout=3)
                status = "healthy" if resp.status_code == 200 else "unhealthy"
            except:
                status = "down"
        else:
            # 本地 Agent，检查进程
            status = "healthy"  # 假设正常
        
        # 记录历史
        if agent_id not in self.health_history:
            self.health_history[agent_id] = []
        self.health_history[agent_id].append({
            "timestamp": datetime.now().isoformat(),
            "status": status
        })
        # 保留最近 10 条
        self.health_history[agent_id] = self.health_history[agent_id][-10:]
        
        return {"agent": agent_id, "status": status, "timestamp": datetime.now().isoformat()}
    
    def check_all(self):
        """检查所有 Agent"""
        results = {}
        for agent_id in agent_registry.list_all():
            results[agent_id] = self.check_agent(agent_id)
        return results
    
    def get_summary(self):
        """获取健康摘要"""
        results = self.check_all()
        healthy = sum(1 for r in results.values() if r.get('status') == 'healthy')
        return {
            "total": len(results),
            "healthy": healthy,
            "unhealthy": len(results) - healthy,
            "details": results
        }

agent_health = AgentHealthCheck()
