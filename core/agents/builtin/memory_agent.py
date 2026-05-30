#!/usr/bin/env python3
"""Memory Agent - Memory Agent 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


from typing import Dict, Optional, Any
from core.agents.base.smart_agent import SmartAgent


class MemoryAgent(SmartAgent):
    """记忆管理 Agent"""

    name = "memory_agent"
    description = "记忆管理"
    version = "2.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._load_agent_config()
        self.memory_store: Dict[str, Any] = {}
        print("💾 MemoryAgent 初始化完成")

    def remember(self, key: str, value: Any) -> bool:
        """记住信息"""
        self.memory_store[key] = value
        return True

    def recall(self, key: str) -> Optional[Any]:
        """回忆记忆"""
        return self.memory_store.get(key)

    def forget(self, key: str) -> bool:
        """忘记信息"""
        if key in self.memory_store:
            del self.memory_store[key]
            return True
        return False

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """处理记忆请求"""
        # 解析用户意图
        if "记住" in user_input:
            # 提取要记住的内容
            import re
            match = re.search(r'记住[:：]?\s*(.+?)\s*(?:是|=|→)\s*(.+)', user_input)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                self.remember(key, value)
                return {
                    "success": True,
                    "response": f"✅ 记住了：{key} = {value}",
                    "agent": self.name,
                    "user_id": self.user_id
                }
        elif "回忆" in user_input or "记得" in user_input:
            import re
            match = re.search(r'(?:回忆|记得)[:：]?\s*(.+)', user_input)
            if match:
                key = match.group(1).strip()
                value = self.recall(key)
                if value:
                    return {
                        "success": True,
                        "response": f"📝 您问的「{key}」是：{value}",
                        "agent": self.name,
                        "user_id": self.user_id
                    }
                else:
                    return {
                        "success": True,
                        "response": f"🤔 我不记得「{key}」。您可以教我：记住 {key} 是 ...",
                        "agent": self.name,
                        "user_id": self.user_id
                    }
        
        return {
            "success": True,
            "response": "我可以帮您记住和回忆信息。例如：记住 临海有什么好玩的 → 临海有江南长城",
            "agent": self.name,
            "user_id": self.user_id
        }

    def can_handle(self, user_input: str) -> dict:
        """判断是否能处理该请求"""
        memory_keywords = ["记住", "忘记", "回忆", "记得", "记录", "保存", "备忘录"]
        score = sum(1 for kw in memory_keywords if kw in user_input)
        return {"can": score >= 1, "confidence": min(score / 3, 1.0)}


# 注意：不创建全局实例（单例模式）

    def remember(self, key: str, value: Any) -> bool:
        """记住信息"""
        self.memory_store[key] = value
        print(f"💾 记住: {key} = {value}")
        return True

    def recall(self, key: str) -> Optional[Any]:
        """回忆信息"""
        result = self.memory_store.get(key)
        print(f"🔍 回忆: {key} -> {result}")
        return result
