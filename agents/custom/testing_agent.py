"""自动化测试 Agent"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from agents.base_agent import BaseAgent

class TestingAgent(BaseAgent):
    name = "testing_agent"
    description = "自动化测试专家，执行测试用例"
    capabilities = ["automated_testing", "regression_testing", "performance_testing"]
    skills = ["calibrated_executor", "quality_gate", "error_analyzer"]
    
    def execute(self, params):
        operation = params.get("operation")
        
        if operation == "run_tests":
            return self._run_tests()
        elif operation == "check_health":
            return self._health_check()
        elif operation == "validate":
            return self._validate(params)
        return {"success": False, "error": "未知操作"}
    
    def _run_tests(self):
        # 运行单元测试
        import subprocess
        result = subprocess.run(["python3", "-m", "pytest", "tests/", "-v"], 
                                capture_output=True, text=True, timeout=60)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def _health_check(self):
        # 检查服务健康
        import requests
        services = [5002, 5003, 5005, 5008, 5010, 5011, 5022]
        results = {}
        for port in services:
            try:
                resp = requests.get(f"http://localhost:{port}/health", timeout=3)
                results[port] = resp.status_code == 200
            except:
                results[port] = False
        return {"success": True, "services": results}
    
    def _validate(self, params):
        return {"success": True, "validated": True}

testing_agent = TestingAgent()
