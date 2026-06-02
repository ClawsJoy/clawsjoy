#!/usr/bin/env python3
"""Chat - Chat 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from core.v5.agent.base import BaseAgent
from core.v5.llm.client import llm
from core.v5.memory.manager import MemoryManager
from typing import Dict
from datetime import datetime
import re


class ChatAgent(BaseAgent):
    """聊天助手 - 完整功能"""
    
    def __init__(self, user_id: str = "default"):
        super().__init__("chat", user_id)
        self.mem_mgr = MemoryManager(user_id, "chat")
    
    def process(self, user_input: str) -> Dict:
        """处理聊天"""
        self.update_stats()

        # 1. 偏好记忆
        if "喜欢" in user_input:
            match = re.search(r'喜欢(.+?)(?:[，。！？]|$)', user_input)
            if match:
                value = match.group(1).strip()
                if value and len(value) < 30 and "什么" not in value:
                    self.mem_mgr.remember_preference("likes", value)
                    self.record_history(user_input, f"记住偏好: {value}")
                    return {
                        "success": True,
                        "type": "chat",
                        "response": f"好的，已记住您喜欢{value}",
                        "user_id": self.user_id
                    }

        # 2. 偏好查询
        if any(q in user_input for q in ["我喜欢喝什么", "我的偏好", "我喜欢什么"]):
            likes = self.mem_mgr.recall_preference("likes")
            if likes:
                response = f"根据记录，您喜欢{likes}"
            else:
                response = "我还没有记住您的偏好，可以告诉我'我喜欢xxx'"

            self.record_history(user_input, response)
            return {
                "success": True,
                "type": "chat",
                "response": response,
                "user_id": self.user_id
            }

        # 3. 问候
        if any(g in user_input for g in ["你好", "您好", "嗨"]):
            response = "您好！我是聊天助手，很高兴为您服务"

        # 4. 道别
        elif any(f in user_input for f in ["再见", "拜拜", "bye"]):
            response = "再见，随时欢迎回来"

        # 5. LLM 对话
        else:
            # 获取相关上下文
            context = self.mem_mgr.search_context(user_input, limit=3)
            context_text = "\n".join(context) if context else ""

            prompt = f"""你是聊天助手。

用户偏好: {self.mem_mgr.preferences}

相关历史: {context_text}

用户: {user_input}

请用温暖、贴心的方式回复:"""

            response = llm.generate(prompt, model_type="chat")

        # 记录到记忆
        self.mem_mgr.add_conversation(user_input, response)
        self.record_history(user_input, response)

        return {
            "success": True,
            "type": "chat",
            "response": response,
            "user_id": self.user_id
        }
