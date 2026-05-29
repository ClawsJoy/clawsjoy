"""智能体基类 - 集成通信能力"""

from typing import Dict, Optional, List, Any
from datetime import datetime
import json
import re

from core.agents.base.communicable_agent import CommunicableAgent
from core.lib.smart_adapter import smart_adapter
from core.lib.skill_loader_v3 import skill_loader
from core.lib.workspace_manager import workspace_manager


class SmartAgent(CommunicableAgent):
    """
    智能体基类 - 高智商 + 通信能力 + 配置驱动决策
    """

    name = "smart_agent"
    description = "智能体基类"
    type = "core"
    version = "2.0.0"

    def __init__(self, user_id: str = "default"):
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

    def _load_smart_config(self) -> dict:
        import yaml
        from pathlib import Path
        config_file = Path("config/smart_agent.yaml")
        if config_file.exists():
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        return {
            "decomposition": {"enabled": True, "max_subtasks": 5},
            "reflection": {"enabled": True, "max_retries": 2},
            "llm": {"enabled": True, "model": "qwen2.5:3b"}
        }

    def get_life_status(self) -> Dict:
        """获取生命状态"""
        return {
            "name": self.name,
            "age_seconds": (datetime.now() - self.birth_time).total_seconds(),
            "stats": self.stats,
            "experiences_count": len(self.experiences),
            "status": "active"
        }

    def record_experience(self, experience: Dict):
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
                f"http://localhost:5002/api/agent/{target}/message",
                json={"message": message, "user_id": self.user_id},
                timeout=30
            )
            return resp.json() if resp.status_code == 200 else {"error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}


smart_agent = SmartAgent()
