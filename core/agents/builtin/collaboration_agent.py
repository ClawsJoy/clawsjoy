"""协作 Agent - 协调多个 Agent 完成任务"""

import time
import requests
from typing import Dict, List, Optional, Any
from core.agents.base.smart_agent import SmartAgent


class CollaborationAgent(SmartAgent):
    """协作 Agent - 多 Agent 协作"""

    name = "collaboration_agent"
    description = "多 Agent 协作协调器"
    version = "2.0.0"

    def __init__(self, user_id: str = "default"):
        self._load_agent_config()
        super().__init__(user_id=user_id)
        self.collaborations: Dict[str, Dict] = {}
        self.records: List[Dict] = []
        self.default_target = "orchestrator"

    def route_to_intelligent(self, user_input: str, previous_agents: List[str] = None) -> Dict:
        """智能路由到合适的 Agent"""
        previous_agents = previous_agents or []

        # 简单的路由逻辑
        target = self.default_target

        if "分析" in user_input or "统计" in user_input:
            target = "analysis_agent"
        elif "代码" in user_input or "编程" in user_input:
            target = "code_agent"
        elif "聊天" in user_input or "对话" in user_input:
            target = "chat_agent"
        elif "执行" in user_input or "运行" in user_input:
            target = "executor_agent"
        elif "决策" in user_input:
            target = "decision_agent"

        # 避免循环调用
        if target in previous_agents:
            target = self.default_target

        print(f"[协作] 转发到: {target}")

        start = time.time()
        try:
            resp = requests.post(
                f"http://localhost:5002/api/agent/{target}/message",
                json={"message": user_input, "user_id": self.user_id},
                timeout=10
            )
            duration_ms = (time.time() - start) * 1000
            result = resp.json() if resp.status_code == 200 else {"error": f"HTTP {resp.status_code}"}

            self._save_record(target, user_input, result, duration_ms)
            return result
        except Exception as e:
            return {"error": str(e), "target": target}

    def _save_record(self, target: str, user_input: str, result: Any, duration_ms: float):
        """保存调用记录"""
        self.records.append({
            "target": target,
            "input": user_input[:100],
            "duration_ms": duration_ms,
            "timestamp": time.time()
        })
        # 保留最近 100 条
        if len(self.records) > 100:
            self.records = self.records[-100:]

    def broadcast_task(self, task: str, data: Dict):
        """广播任务给所有订阅者"""
        try:
            from core.lib.agent_bus import get_bus
            bus = get_bus()
            bus.publish(self.name, "collaboration.task", {
                "task": task,
                "data": data,
                "from": self.name
            })
        except Exception as e:
            print(f"[协作] 广播失败: {e}")



    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """处理协作请求"""
        # 默认协作逻辑：路由到 orchestrator
        from core.agents.builtin.orchestrator import OrchestratorAgent
        orch = OrchestratorAgent(self.user_id)
        return orch.dispatch(user_input, "orchestrator")

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            "name": self.name,
            "version": self.version,
            "records_count": len(self.records),
            "user_id": self.user_id
        }


# 全局实例
# collaboration_agent = CollaborationAgent()  # 注释：改为按需创建
