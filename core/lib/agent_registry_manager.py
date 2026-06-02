#!/usr/bin/env python3
"""Agent Registry Manager - Agent Registry Manager 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import yaml
from pathlib import Path
from typing import Dict, List, Optional
from core.lib.vector_knowledge_center import vector_knowledge_center


class AgentRegistryManager:
    """Agent 注册管理器"""

    def __init__(self):
        self.agents_work_dir = Path("agents")

    def discover_agents(self, user_id: str = "system") -> List[Dict]:
        """发现并注册所有 Agent"""
        registered = []
        
        if not self.agents_work_dir.exists():
            return registered
        
        for agent_dir in self.agents_work_dir.iterdir():
            if not agent_dir.is_dir():
                continue
            
            config_file = agent_dir / "config.yaml"
            if not config_file.exists():
                continue
            
            try:
                with open(config_file, 'r') as f:
                    config = yaml.safe_load(f)
                    agent_info = config.get('agent', {})
                    
                    # 生成能力描述
                    role = agent_info.get('role', {})
                    capabilities = agent_info.get('capabilities', [])
                    
                    capability_desc = f"""
Agent名称: {agent_info.get('name', agent_dir.name)}
角色: {role.get('title', agent_dir.name)}
职责: {', '.join(capabilities) if capabilities else role.get('responsibilities', [])}
描述: {agent_info.get('description', '')}
"""
                    
                    # 注册到向量库
                    vector_knowledge_center.add_agent_capability(
                        agent_name=agent_dir.name,
                        capability_desc=capability_desc.strip(),
                        user_id=user_id
                    )
                    registered.append({
                        "name": agent_dir.name,
                        "status": "registered"
                    })
                    print(f"✅ 注册 Agent: {agent_dir.name}")
            except Exception as e:
                print(f"❌ 注册失败 {agent_dir.name}: {e}")
        
        return registered

    def register_new_agent(self, agent_name: str, config: Dict, user_id: str = "system") -> bool:
        """注册新的自定义 Agent"""
        try:
            # 创建工作区目录
            agent_dir = self.agents_work_dir / agent_name
            agent_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存配置
            config_file = agent_dir / "config.yaml"
            with open(config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            # 创建 Agent 代码文件模板
            agent_file = agent_dir / "agent.py"
            if not agent_file.exists():
                agent_file.write_text(f'''
"""自定义 Agent: {agent_name}"""

from typing import Dict, Optional
from core.agents.base.smart_agent import SmartAgent


class {agent_name[0].upper() + agent_name[1:]}Agent(SmartAgent):
    name = "{agent_name}"
    description = "{config.get('agent', {}).get('description', '自定义Agent')}"
    
    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._load_agent_config()
    
    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        return {{
            "success": True,
            "response": f"[{self.name}] 收到: {{user_input}}",
            "agent": self.name,
            "user_id": self.user_id
        }}
''')
            
            # 注册能力
            role = config.get('agent', {}).get('role', {})
            capabilities = config.get('agent', {}).get('capabilities', [])
            capability_desc = f"角色: {role.get('title', agent_name)} 职责: {', '.join(capabilities)}"
            
            vector_knowledge_center.add_agent_capability(
                agent_name=agent_name,
                capability_desc=capability_desc,
                user_id=user_id
            )
            return True
        except Exception as e:
            print(f"注册失败: {e}")
            return False

    def list_registered_agents(self, user_id: str = "system") -> List[Dict]:
        """列出已注册的 Agent"""
        return vector_knowledge_center.list_agent_capabilities(user_id)


agent_registry = AgentRegistryManager()
