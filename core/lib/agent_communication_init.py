"""Agent 通信系统初始化模块"""
import threading
from typing import Dict, Any

from core.lib.agent_bus import get_bus

# Agent 能力与主题映射
AGENT_TOPICS = {
    "orchestrator": ["task.plan", "task.schedule", "workflow.start", "workflow.complete"],
    "video_agent": ["task.video", "task.video.create", "task.video.edit", "task.video.subtitle"],
    "code_agent": ["task.code", "task.code.generate", "task.code.review", "task.code.debug"],
    "analysis_agent": ["task.analyze", "task.analyze.data", "task.analyze.health", "task.analyze.trend"],
    "decision_agent": ["task.decision", "task.decision.optimize", "task.decision.schedule"],
    "youtube_agent": ["task.youtube", "task.youtube.upload", "task.youtube.analyze", "task.youtube.optimize"],
    "translate_agent": ["task.translate", "task.translate.document"],
    "chat_agent": ["task.chat", "task.chat.reply", "task.chat.understand"],
    "memory_manager": ["task.memory", "task.memory.store", "task.memory.search", "task.memory.vector"],
    "security_agent": ["task.security", "task.security.check", "task.security.audit"],
    "personal_butler": ["task.butler", "task.butler.reminder", "task.butler.schedule"],
}

# 全局单例
_comm_manager = None


class AgentCommunicationManager:
    """Agent通信管理器"""

    def __init__(self):
        self.bus = get_bus()
        self.initialized = False

    def init_communication(self):
        """初始化所有Agent的通信能力"""
        if self.initialized:
            return True

        print("=" * 50)
        print("🔧 初始化 Agent 通信系统")
        print("=" * 50)

        for agent_name, topics in AGENT_TOPICS.items():
            for topic in topics:
                self.bus.subscribe(agent_name, topic)

        self.initialized = True
        self._print_status()
        return True

    def _print_status(self):
        status = self.bus.get_status()
        print("\n📊 通信系统状态:")
        print(f"   - 主题数: {status['topics']}")
        print(f"   - 订阅总数: {status['total_subscriptions']}")
        print(f"   - 队列大小: {status['queue_size']}")
        print(f"   - 历史消息: {status['history_size']}")
        print(f"   - 处理器数: {status['handlers']}")

    def route_task(self, task_type: str, task_content: Dict) -> str:
        """路由任务到对应的Agent"""
        routing = {
            "video": "video_agent", "code": "code_agent", "analyze": "analysis_agent",
            "decision": "decision_agent", "youtube": "youtube_agent", "translate": "translate_agent",
            "chat": "chat_agent", "memory": "memory_manager", "security": "security_agent",
            "butler": "personal_butler", "plan": "orchestrator"
        }
        agent = routing.get(task_type, "orchestrator")
        topic = f"task.{task_type}"
        message_id = self.bus.publish("gateway", topic, {"task": task_content, "task_type": task_type})
        return message_id


def get_comm_manager():
    """获取通信管理器单例"""
    global _comm_manager
    if _comm_manager is None:
        _comm_manager = AgentCommunicationManager()
    return _comm_manager


def init_agent_communication():
    """初始化Agent通信"""
    manager = get_comm_manager()
    return manager.init_communication()
