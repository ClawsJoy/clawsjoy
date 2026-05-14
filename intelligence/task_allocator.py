"""智能任务分配器 - 动态分配任务给最合适的Agent"""
import json
import requests
from datetime import datetime
from collections import defaultdict
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

class SmartTaskAllocator:
    """智能任务分配器"""
    
    def __init__(self):
        self.agent_performance = defaultdict(list)
        self.task_history = []
        
    def get_agent_capabilities(self) -> dict:
        """获取所有Agent能力"""
        try:
            resp = requests.get("http://localhost:5005/agents", timeout=3)
            if resp.status_code == 200:
                agents = resp.json().get('agents', [])
                # 根据名称推断能力
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
        except:
            pass
        return {}
    
    def record_performance(self, agent_name: str, task: str, success: bool, duration: float):
        """记录Agent表现"""
        self.agent_performance[agent_name].append({
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "success": success,
            "duration": duration
        })
    
    def get_best_agent(self, task_type: str) -> str:
        """获取最适合的Agent"""
        capabilities = self.get_agent_capabilities()
        
        # 计算每个Agent的得分
        scores = {}
        for agent, caps in capabilities.items():
            score = 0
            # 能力匹配
            if task_type in caps:
                score += 50
            
            # 历史成功率
            history = self.agent_performance.get(agent, [])
            if history:
                success_rate = sum(1 for h in history if h['success']) / len(history)
                score += success_rate * 30
            
            # 最近表现
            recent = [h for h in history if h.get('duration', 0) < 5]
            if recent:
                recent_success = sum(1 for h in recent if h['success']) / len(recent)
                score += recent_success * 20
            
            scores[agent] = score
        
        if scores:
            best = max(scores, key=scores.get)
            return best
        
        return list(capabilities.keys())[0] if capabilities else "SupervisorAgent"
    
    def allocate(self, task: str, task_type: str = "general") -> dict:
        """分配任务"""
        best_agent = self.get_best_agent(task_type)
        
        allocation = {
            "task": task,
            "task_type": task_type,
            "assigned_agent": best_agent,
            "timestamp": datetime.now().isoformat(),
            "reason": f"基于能力匹配和历史表现"
        }
        
        self.task_history.append(allocation)
        
        # 尝试执行
        try:
            result = self._execute_task(best_agent, task)
            self.record_performance(best_agent, task, result.get('success', False), result.get('duration', 0))
            allocation["result"] = result
        except Exception as e:
            allocation["error"] = str(e)
        
        return allocation
    
    def _execute_task(self, agent: str, task: str) -> dict:
        """执行任务"""
        import time
        start = time.time()
        
        try:
            resp = requests.post("http://localhost:5005/execute", 
                                json={"goal": task}, timeout=30)
            duration = time.time() - start
            if resp.status_code == 200:
                return {"success": True, "duration": duration, "result": resp.json()}
            else:
                return {"success": False, "duration": duration, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"success": False, "duration": time.time() - start, "error": str(e)}

if __name__ == "__main__":
    allocator = SmartTaskAllocator()
    result = allocator.allocate("监控系统状态", "supervision")
    print(json.dumps(result, indent=2, ensure_ascii=False))
