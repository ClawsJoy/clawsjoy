"""协作 Agent - 多 Agent 协作"""

import time
import requests
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from core.agents.base.smart_agent import SmartAgent
from core.lib.workspace_manager import workspace_manager


class CollaborationAgent(SmartAgent):
    """协作Agent"""

    name = "collaboration_agent"
    description = "多Agent协作"
    type = "core"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self.behavior = workspace_manager.get_behavior_config("collaboration_agent")
        print(f"🤝 协作Agent 初始化完成")

    def _save_record(self, to_agent: str, request: str, response: dict, duration_ms: float):
        """保存通信记录"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "from": self.name,
            "to": to_agent,
            "request": request,
            "response": response,
            "duration_ms": duration_ms,
            "user_id": self.user_id
        }
        log_dir = Path("data/exchange")
        log_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        with open(log_dir / filename, 'w') as f:
            json.dump(record, f, indent=2)

    def process(self, user_input: str, context=None) -> Dict:
        print(f"[协作] 收到: {user_input}")

        routing = self.behavior.get('routing', {}) if self.behavior else {}
        rules = routing.get('rules', [])
        default_target = routing.get('default_target', 'chat_agent')

        target = default_target
        for rule in rules:
            for intent in rule.get('intent', []):
                if intent in user_input:
                    target = rule.get('target', default_target)
                    break
            if target != default_target:
                break

        print(f"[协作] 转发到: {target}")

        start = time.time()
        resp = requests.post(
            f"http://localhost:5002/api/agent/{target}/message",
            json={"message": user_input, "user_id": self.user_id},
            timeout=10
        )
        duration_ms = (time.time() - start) * 1000
        result = resp.json() if resp.status_code == 200 else {"error": f"HTTP {resp.status_code}"}

        self._save_record(target, user_input, result, duration_ms)

        return result


collaboration_agent = CollaborationAgent()

    def broadcast_task(self, task: str, data: Dict):
        """广播任务给所有订阅者"""
        from core.lib.agent_bus import get_bus
        bus = get_bus()
        bus.publish(self.name, "collaboration.task", {
            "task": task,
            "data": data,
            "from": self.name
        })
