"""具备四种通信能力的 Agent 基类"""

from typing import Dict, Optional
from core.agents.base.base_agent import BaseAgent
from core.lib.agent_bus import get_bus
from core.lib.agent_communication import agent_comm, MessageType
from core.lib.file_queue import to_decision, to_chat


class CommunicableAgent(BaseAgent):
    """具备四种通信能力的 Agent"""

    def http_call(self, target: str, message: str, timeout: int = 30) -> dict:
        """HTTP 同步调用"""
        import requests
        try:
            resp = requests.post(
                f"http://localhost:5002/api/agent/{target}/message",
                json={"message": message, "user_id": self.user_id},
                timeout=timeout
            )
            return resp.json() if resp.status_code == 200 else {"error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def bus_publish(self, topic: str, data: dict):
        """Agent Bus 发布事件"""
        bus = get_bus()
        bus.publish(self.name, topic, data)

    def bus_subscribe(self, topic: str, handler):
        """Agent Bus 订阅事件"""
        bus = get_bus()
        bus.subscribe(self.name, topic)
        bus.register_handler(topic, handler)

    def queue_send_to_decision(self, message: dict) -> str:
        """发送任务到决策师队列"""
        return to_decision.send("decision_agent", {
            "from": self.name,
            "message": message,
            "user_id": self.user_id
        })

    def queue_send_to_chat(self, message: dict) -> str:
        """发送响应到聊天队列"""
        return to_chat.send("butler", {
            "from": self.name,
            "message": message,
            "user_id": self.user_id
        })

    def queue_receive_from_decision(self) -> Optional[dict]:
        """从决策师队列接收任务"""
        return to_decision.receive("decision_agent")

    def comm_send(self, to: str, action: str, data: dict) -> str:
        """Agent Communication 点对点发送"""
        return agent_comm.send(self.name, to, {"action": action, "data": data}, MessageType.REQUEST)

    def comm_broadcast(self, event_type: str, data: dict) -> str:
        """Agent Communication 广播"""
        return agent_comm.send_broadcast(self.name, event_type, data)
