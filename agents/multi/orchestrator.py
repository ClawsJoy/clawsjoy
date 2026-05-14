"""多智能体协作编排器"""

import sys
import json
import importlib
from pathlib import Path

sys.path.insert(0, '/mnt/d/clawsjoy')

class MultiAgentOrchestrator:
    def __init__(self):
        self.agents = {}
        self._discover_agents()
        print(f"🤝 多智能体编排器初始化")
        print(f"   可用 Agent: {len(self.agents)} 个")
    
    def _discover_agents(self):
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
                            self.agents[name] = instance
                            print(f"   ✅ 加载: {name}")
                        except Exception as e:
                            print(f"   ⚠️ {name} 实例化失败: {e}")
            except Exception as e:
                print(f"   ⚠️ 跳过 {py_file.name}: {str(e)[:50]}")
    
    def _run_agent(self, agent, task):
        """安全调用 Agent"""
        try:
            if hasattr(agent, 'run'):
                # 检查 run 方法参数
                import inspect
                sig = inspect.signature(agent.run)
                if len(sig.parameters) == 1:
                    return agent.run(task)
                else:
                    return agent.run()
            elif hasattr(agent, 'execute'):
                return agent.execute({"task": task})
            else:
                return {"message": f"{agent.__class__.__name__} 已处理"}
        except Exception as e:
            return {"error": str(e), "agent": agent.__class__.__name__}
    
    def execute(self, goal: str) -> dict:
        results = {}
        
        # 根据关键词选择 Agent
        for name, agent in self.agents.items():
            if 'Supervisor' in name and ('监控' in goal or '监控' in goal):
                results[name] = self._run_agent(agent, goal)
            elif 'Learning' in name and ('学习' in goal or 'learn' in goal.lower()):
                results[name] = self._run_agent(agent, goal)
            elif 'Ops' in name and ('运维' in goal or 'ops' in goal.lower()):
                results[name] = self._run_agent(agent, goal)
        
        if not results:
            # 默认执行所有 Agent（简单测试）
            for name, agent in list(self.agents.items())[:3]:
                results[name] = self._run_agent(agent, goal)
        
        return {"success": True, "goal": goal, "results": results}
    
    def list_agents(self):
        return list(self.agents.keys())

if __name__ == '__main__':
    orch = MultiAgentOrchestrator()
    print(f"\n可用 Agent: {orch.list_agents()}")
    result = orch.execute("监控系统状态")
    print(f"\n执行结果: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
