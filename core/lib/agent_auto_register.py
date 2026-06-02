#!/usr/bin/env python3
"""Agent Auto Register - Agent Auto Register 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import yaml
from pathlib import Path
from typing import Dict, List, Optional


class AgentAutoRegister:
    """自动注册 Agent - 扫描 config/agents/registry/ 目录"""
    
    def __init__(self):
        self.registry_dir = Path("config/agents/registry")
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self._agents: Dict = {}
        self._load_all()
    
    def _load_all(self):
        """加载所有 Agent 配置"""
        for config_file in self.registry_dir.glob("*.yaml"):
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                    agent_name = config.get('name')
                    if agent_name:
                        self._agents[agent_name] = config
                        print(f"   ✅ 自动注册 Agent: {agent_name} v{config.get('version', '1.0')}")
            except Exception as e:
                print(f"   ❌ 加载失败 {config_file}: {e}")
    
    def get_agent_config(self, agent_name: str) -> Optional[Dict]:
        """获取 Agent 配置"""
        return self._agents.get(agent_name)
    
    def list_agents(self) -> List[str]:
        """列出所有已注册 Agent"""
        return list(self._agents.keys())
    
    def register_agent(self, config: Dict) -> bool:
        """动态注册新 Agent（开发者 API）"""
        agent_name = config.get('name')
        if not agent_name:
            return False

        config_file = self.registry_dir / f"{agent_name}.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config, f, allow_unicode=True, sort_keys=False)

        self._agents[agent_name] = config
        print(f"   ✅ 动态注册 Agent: {agent_name}")
        return True
    
    def unregister_agent(self, agent_name: str) -> bool:
        """注销 Agent"""
        config_file = self.registry_dir / f"{agent_name}.yaml"
        if config_file.exists():
            config_file.unlink()
            if agent_name in self._agents:
                del self._agents[agent_name]
            print(f"   🗑️ 注销 Agent: {agent_name}")
            return True
        return False


# 全局实例
agent_auto_register = AgentAutoRegister()
