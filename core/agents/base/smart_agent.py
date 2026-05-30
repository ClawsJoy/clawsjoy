#!/usr/bin/env python3
"""Smart Agent - Smart Agent 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


from typing import Dict, Optional, List, Any
from datetime import datetime
import json
import re

from core.agents.base.communicable_agent import CommunicableAgent
from core.lib.smart_adapter import smart_adapter
from core.lib.skill_loader_v3 import skill_loader
from core.lib.workspace_manager import workspace_manager
from core.lib.unified_config import unified_config


class SmartAgent(CommunicableAgent):
    """
    智能体基类 - 高智商 + 通信能力 + 配置驱动决策
    """

    name = "smart_agent"
    description = "智能体基类"
    type = "core"
    version = "2.0.0"

    def __init__(self, user_id: str = "default") -> None:
        super().__init__(user_id=user_id)
        self.birth_time = datetime.now()
        self.stats = {
            "tasks_handled": 0,
            "success_count": 0,
            "fail_count": 0,
            "total_response_time": 0,
            "learning_count": 0
        }
        self.experiences = []
        self.smart_config = self._load_smart_config()
        self.behavior = workspace_manager.get_behavior_config(self.name)
        print(f"[{self.name}] 智能体初始化完成 v{self.version}")

    def _load_smart_config(self) -> None:
        import yaml
        from pathlib import Path
        config_file = Path("config/smart_agent.yaml")
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        return {
            "decomposition": {"enabled": True, "max_subtasks": 5},
            "reflection": {"enabled": True, "max_retries": 2},
            "llm": {"enabled": True, "model": unified_config.get("llm.fast_model", "qwen2.5:3b")}
        }

    def get_life_status(self) -> Any:
        """获取生命状态"""
        return {
            "name": self.name,
            "age_seconds": (datetime.now() - self.birth_time).total_seconds(),
            "stats": self.stats,
            "experiences_count": len(self.experiences),
            "status": "active"
        }

    def record_experience(self, experience: Dict) -> Any:
        """记录经验"""
        experience["timestamp"] = datetime.now().isoformat()
        self.experiences.append(experience)
        self.stats["learning_count"] += 1
        if len(self.experiences) > 100:
            self.experiences = self.experiences[-100:]

    def share_experience(self, target_agent: str, experience_id: int) -> bool:
        """分享经验"""
        if experience_id >= len(self.experiences):
            return False
        exp = self.experiences[experience_id]
        self.bus_publish(f"agent.{target_agent}.experience", exp)
        return True



    def http_call(self, target: str, message: str) -> dict:
        """HTTP 调用其他 Agent"""
        import requests
        try:
            resp = requests.post(
                f"http://{unified_config.get("services.gateway.host", "localhost")}:{unified_config.get("services.gateway.port", 5002)}/api/agent/{target}/message",
                json={"message": message, "user_id": self.user_id},
                timeout=30
            )
            return resp.json() if resp.status_code == 200 else {"error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def handle(self, user_input: str, context: dict = None) -> dict:
        """处理用户输入（默认实现）"""
        return self.process(user_input, context)

    def learn(self, feedback: dict) -> None:
        """学习反馈（默认实现）"""
        self.stats["learning_count"] += 1
        return True

    def get_memory(self, key: str, default=None) -> Any:
        """获取记忆"""
        return self._memory.get(key, default)

    def set_memory(self, key: str, value) -> Any:
        """设置记忆"""
        self._memory[key] = value
        self._save_memory()

    def get_stats(self) -> None:
        """获取统计信息"""
        return {
            "name": self.name,
            "version": self.version,
            "tasks_handled": self.stats.get("tasks_handled", 0),
            "success_count": self.stats.get("success_count", 0),
            "learning_count": self.stats.get("learning_count", 0)
        }

    def _save_memory(self) -> None:
        """保存记忆到文件"""
        import json
        from pathlib import Path
        memory_file = Path(self.memory_dir) / "memory.json"
        try:
            with open(memory_file, 'w') as f:
                json.dump(self._memory, f, indent=2)
        except Exception as e:
            print(f"保存记忆失败: {e}")

    def get_skill(self, skill_name: str) -> None:
        """获取技能"""
        return self.skills.get(skill_name, {})

    def has_capability(self, capability: str) -> bool:
        """检查是否有特定能力"""
        return capability in self.capabilities

    def load_llm_config(self):
        """从工作区加载 LLM 配置"""
        import yaml
        from pathlib import Path
        
        self.llm_model = unified_config.get("llm.fast_model", "qwen2.5:3b")
        self.llm_temperature = 0.7
        self.llm_max_tokens = 1024
        
        config_path = Path(f"agents/{self.name}/config.yaml")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    agent_cfg = config.get('agent', {})
                    llm_cfg = agent_cfg.get('llm', {})
                    self.llm_model = llm_cfg.get('model', self.llm_model)
                    self.llm_temperature = llm_cfg.get('temperature', self.llm_temperature)
                    self.llm_max_tokens = llm_cfg.get('max_tokens', self.llm_max_tokens)
                    print(f"[{self.name}] 使用模型: {self.llm_model}")
            except Exception as e:
                print(f"[{self.name}] 加载配置失败: {e}")

    def _load_agent_config(self):
        """加载 Agent 工作区配置（在 __init__ 中调用）"""
        import yaml
        from pathlib import Path
        
        # 默认值
        self.llm_model = unified_config.get("llm.fast_model", "qwen2.5:3b")
        self.llm_temperature = 0.7
        self.llm_max_tokens = 1024
        self.agent_role = None
        self.capabilities = []
        
        config_path = Path(f"agents/{self.name}/config.yaml")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    agent_cfg = config.get('agent', {})
                    
                    # 加载角色信息
                    self.agent_role = agent_cfg.get('role', {})
                    self.capabilities = self.agent_role.get('responsibilities', [])
                    
                    # 加载 LLM 配置
                    llm_cfg = agent_cfg.get('llm', {})
                    self.llm_model = llm_cfg.get('model', self.llm_model)
                    self.llm_temperature = llm_cfg.get('temperature', self.llm_temperature)
                    self.llm_max_tokens = llm_cfg.get('max_tokens', self.llm_max_tokens)
                    
                    print(f"[{self.name}] 使用模型: {self.llm_model}")
            except Exception as e:
                print(f"[{self.name}] 加载配置失败: {e}")

    def register_capability(self):
        """注册 Agent 能力到向量库（用于智能路由）"""
        try:
            from core.lib.vector_knowledge_center import vector_knowledge_center
            
            # 生成能力描述
            capability_desc = f"""
            角色: {getattr(self, 'agent_role', {}).get('title', self.name)}
            职责: {', '.join(getattr(self, 'capabilities', []))}
            描述: {self.description}
            """
            
            vector_knowledge_center.add_agent_capability(
                agent_name=self.name,
                capability_desc=capability_desc,
                user_id=self.user_id
            )
            print(f"[{self.name}] 能力已注册到向量库")
        except Exception as e:
            print(f"[{self.name}] 能力注册失败: {e}")

    def register_capability(self):
        """注册 Agent 能力到向量库（用于智能路由）"""
        try:
            from core.lib.vector_knowledge_center import vector_knowledge_center
            
            # 生成能力描述
            role = getattr(self, 'agent_role', {})
            capabilities = getattr(self, 'capabilities', [])
            
            capability_desc = f"""
Agent名称: {self.name}
角色: {role.get('title', self.name) if role else self.name}
职责: {', '.join(capabilities) if capabilities else self.description}
描述: {self.description}
"""
            
            vector_knowledge_center.add_agent_capability(
                agent_name=self.name,
                capability_desc=capability_desc.strip(),
                user_id=self.user_id
            )
            print(f"[{self.name}] 能力已注册到向量库")
        except Exception as e:
            print(f"[{self.name}] 能力注册失败: {e}")
