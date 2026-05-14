"""增强版多智能体协作器 - 支持 Agent 间通信和任务链"""

import json
import importlib
import threading
from queue import Queue
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import sys

sys.path.insert(0, '/mnt/d/clawsjoy')

class EnhancedOrchestrator:
    def __init__(self):
        self.agents = {}
        self.task_queue = Queue()
        self.results = {}
        self.communication_log = []
        self._discover_agents()
        print(f"🤝 增强版多智能体编排器")
        print(f"   可用 Agent: {len(self.agents)} 个")
    
    def _discover_agents(self):
        """发现并加载 Agent"""
        agents_dir = Path("/mnt/d/clawsjoy/agents")
        
        for py_file in agents_dir.glob("*_agent.py"):
            if py_file.name.startswith('__'):
                continue
            
            try:
                module_name = f"agents.{py_file.stem}"
                module = importlib.import_module(module_name)
                
                for name, obj in module.__dict__.items():
                    if name.endswith('Agent') and isinstance(obj, type):
                        try:
                            instance = obj()
                            self.agents[name] = {
                                'instance': instance,
                                'name': name,
                                'type': self._get_agent_type(name),
                                'status': 'idle'
                            }
                            print(f"   ✅ 加载: {name}")
                        except Exception as e:
                            print(f"   ⚠️ {name} 实例化失败: {e}")
            except Exception as e:
                pass
    
    def _get_agent_type(self, name):
        if 'Supervisor' in name: return 'supervisor'
        if 'Learning' in name: return 'learning'
        if 'Ops' in name: return 'ops'
        if 'Security' in name: return 'security'
        if 'Cleaner' in name: return 'cleaner'
        return 'general'
    
    def delegate_task(self, from_agent: str, to_agent: str, task: str) -> Dict:
        """Agent 间任务委托"""
        if to_agent not in self.agents:
            return {"error": f"Agent {to_agent} not found"}
        
        self.communication_log.append({
            "from": from_agent,
            "to": to_agent,
            "task": task,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"   📨 {from_agent} → {to_agent}: {task[:50]}")
        
        return self._run_agent(self.agents[to_agent]['instance'], task)
    
    def _run_agent(self, agent, task):
        """运行 Agent"""
        try:
            if hasattr(agent, 'run'):
                import inspect
                sig = inspect.signature(agent.run)
                if len(sig.parameters) == 1:
                    return agent.run(task)
                else:
                    return agent.run()
            elif hasattr(agent, 'execute'):
                return agent.execute({"task": task})
            return {"message": f"{agent.__class__.__name__} 已处理"}
        except Exception as e:
            return {"error": str(e)}
    
    def create_task_chain(self, tasks: List[Dict]) -> Dict:
        """创建任务链（多步协作）"""
        results = {}
        context = {}
        
        for i, task in enumerate(tasks):
            agent_name = task.get('agent')
            action = task.get('action', '')
            params = task.get('params', {})
            
            if agent_name not in self.agents:
                results[f"step_{i+1}"] = {"error": f"Agent not found: {agent_name}"}
                continue
            
            # 合并上下文
            if context:
                params['context'] = context
            
            print(f"🔗 步骤 {i+1}: {agent_name} - {action[:40]}")
            result = self._run_agent(self.agents[agent_name]['instance'], action)
            results[f"step_{i+1}"] = {
                "agent": agent_name,
                "action": action,
                "result": result
            }
            
            # 传递结果到下一步
            if result and result.get('success'):
                context[f"step_{i+1}_result"] = result
        
        return {"success": True, "chain_results": results, "context": context}
    
    def parallel_execute(self, tasks: List[Dict]) -> Dict:
        """并行执行多个 Agent 任务"""
        results = {}
        threads = []
        result_lock = threading.Lock()
        
        def run_task(agent_name, action, task_id):
            if agent_name not in self.agents:
                with result_lock:
                    results[task_id] = {"error": f"Agent not found: {agent_name}"}
                return
            
            result = self._run_agent(self.agents[agent_name]['instance'], action)
            with result_lock:
                results[task_id] = {
                    "agent": agent_name,
                    "action": action,
                    "result": result
                }
        
        for i, task in enumerate(tasks):
            agent_name = task.get('agent')
            action = task.get('action', '')
            t = threading.Thread(target=run_task, args=(agent_name, action, f"task_{i+1}"))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        return {"success": True, "parallel_results": results}
    
    def execute(self, goal: str) -> Dict:
        """智能执行任务"""
        results = {}
        
        # 根据目标类型选择执行策略
        if "监控" in goal or "monitor" in goal.lower():
            # 单 Agent 执行
            agent = self.agents.get("SupervisorAgent", {}).get('instance')
            if agent:
                results["supervisor"] = self._run_agent(agent, goal)
        
        elif "学习" in goal or "learn" in goal.lower():
            agent = self.agents.get("TrueLearningAgent", {}).get('instance')
            if agent:
                results["learning"] = self._run_agent(agent, goal)
        
        elif "运维" in goal or "ops" in goal.lower():
            agent = self.agents.get("SmartOpsAgent", {}).get('instance')
            if agent:
                results["ops"] = self._run_agent(agent, goal)
        
        elif "链" in goal or "chain" in goal.lower():
            # 任务链示例
            tasks = [
                {"agent": "SupervisorAgent", "action": "检查系统状态"},
                {"agent": "SmartOpsAgent", "action": "执行维护"},
                {"agent": "SimpleLearningAgent", "action": "记录结果"}
            ]
            results = self.create_task_chain(tasks)
        
        elif "并行" in goal or "parallel" in goal.lower():
            tasks = [
                {"agent": "SupervisorAgent", "action": "检查API"},
                {"agent": "SecurityAgent", "action": "检查安全"},
                {"agent": "CleanerAgent", "action": "清理临时文件"}
            ]
            results = self.parallel_execute(tasks)
        
        else:
            # 默认：执行所有 Agent
            for name, info in list(self.agents.items())[:3]:
                results[name] = self._run_agent(info['instance'], goal)
        
        return {"success": True, "goal": goal, "results": results}
    
    def get_communication_log(self):
        return {"logs": self.communication_log[-20:]}

enhanced_orchestrator = EnhancedOrchestrator()

if __name__ == '__main__':
    # 测试任务链
    print("\n" + "="*50)
    print("测试任务链")
    print("="*50)
    result = enhanced_orchestrator.create_task_chain([
        {"agent": "SupervisorAgent", "action": "检查系统"},
        {"agent": "SmartOpsAgent", "action": "执行维护"}
    ])
    print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
