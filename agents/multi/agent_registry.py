"""统一 Agent 注册中心 - 整合所有 Agent"""

import importlib
import inspect
from pathlib import Path
from typing import Dict, List

class AgentRegistry:
    def __init__(self):
        self.agents = {}
        self._discover_agents()
    
    def _discover_agents(self):
        """自动发现并注册所有 Agent"""
        agents_dir = Path(__file__).parent.parent
        
        for py_file in agents_dir.glob("*_agent.py"):
            if py_file.name.startswith('__'):
                continue
            
            try:
                module_name = f"agents.{py_file.stem}"
                module = importlib.import_module(module_name)
                
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if name.endswith('Agent') and name != 'BaseAgent':
                        if hasattr(obj, 'execute') or hasattr(obj, 'run'):
                            self.agents[name] = {
                                "class": obj,
                                "module": module_name,
                                "name": name,
                                "file": str(py_file)
                            }
                            print(f"✅ 发现 Agent: {name}")
            except Exception as e:
                print(f"⚠️ 加载 {py_file.name} 失败: {e}")
    
    def get_agent(self, name: str):
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        return list(self.agents.keys())

agent_registry = AgentRegistry()
