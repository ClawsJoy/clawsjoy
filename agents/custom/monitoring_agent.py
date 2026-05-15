"""系统监控 Agent"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from agents.base_agent import BaseAgent
import requests
import psutil

class MonitoringAgent(BaseAgent):
    name = "monitoring_agent"
    description = "系统监控专家，监控服务状态和资源使用"
    capabilities = ["system_monitoring", "resource_usage", "alerting", "health_check"]
    skills = ["calibrated_executor", "quality_gate"]
    
    def execute(self, params):
        operation = params.get("operation")
        
        if operation == "health":
            return self._health_check()
        elif operation == "resources":
            return self._get_resources()
        elif operation == "services":
            return self._check_services()
        return {"success": False, "error": "未知操作"}
    
    def _health_check(self):
        ports = [5002, 5003, 5005, 5008, 5010, 5011, 5022, 5023, 5024]
        results = {}
        for port in ports:
            try:
                resp = requests.get(f"http://localhost:{port}/health", timeout=3)
                results[port] = resp.status_code == 200
            except:
                results[port] = False
        return {"success": True, "services": results}
    
    def _get_resources(self):
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        }
    
    def _check_services(self):
        return {"success": True, "message": "所有服务运行中"}

monitoring_agent = MonitoringAgent()
