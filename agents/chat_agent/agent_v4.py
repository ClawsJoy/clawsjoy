#!/usr/bin/env python3
"""ChatAgent v5.0 - 精简对话助手

职责:
- 对话（委托给 chat_engine）
- 方言处理
- 名字记忆
- 简单情感检测

删除:
- 批处理缓冲区（Gateway 应做）
- 主动服务评估（AgentCortex 应做）
- 语义理解注入（AgentCortex 应做）
- 灵魂注入（移到专用模块）
"""

import re
from typing import Dict, Optional, Tuple
from datetime import datetime

from core.agents.business.business_agent import BusinessAgent
from core.lib.dialect.dialect_helper import get_dialect_helper


class ChatAgentV4(BusinessAgent):
    name = "chat_agent_v4"
    description = "智慧对话助手"
    version = "5.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)

        self._history: list = []
        self._max_history = 10
        self._session_id: Optional[str] = None
        self._chat_engine = None

        print(f"💬 ChatAgent v{self.version} 启动")

    @property
    def chat_engine(self):
        if self._chat_engine is None:
            try:
                from core.lib.chat_engine import chat_engine
                self._chat_engine = chat_engine
            except Exception as e:
                print(f"[ChatAgent] 加载对话引擎失败: {e}")
        return self._chat_engine

    # ====================================================================
    #  入口
    # ====================================================================

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        if context and "session_id" in context:
            self._session_id = context["session_id"]
        return super().process(user_input, context)

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)

    # ====================================================================
    #  核心业务
    # ====================================================================

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        original = user_input
        session_id = self._session_id or "default"

        # 1. 方言处理
        dialect = get_dialect_helper(self.user_id)
        has_dialect = dialect.has_dialect(user_input)
        if has_dialect:
            user_input, _ = dialect.to_standard(user_input)

        # 2. 名字提取
        user_name = self._extract_name(original)

        # 3. 简单情感
        emotion = self._detect_emotion(user_input)

        # 4. 记忆
        memories = self._load_memories(session_id)

        # 5. 对话引擎
        response = self._chat(user_input, original, session_id, emotion, memories)

        # 6. 方言回译
        if has_dialect and response:
            try:
                response, _ = dialect.to_dialect(response)
            except Exception as e:
                print(f"[ChatAgent] 方言回译失败: {e}")

        # 7. 记录
        self._update_history(original, response)
        self._save_memory(session_id, original, response)

        return self._response(response)

    # ====================================================================
    #  名字提取
    # ====================================================================

    def _extract_name(self, text: str) -> str:
        """从输入中提取用户名字"""
        user_name = self.recall_forever("user_name") or ""
        name_match = re.search(
            r'(?:我叫|叫我|可以叫我|英文名叫)[：: ]*(\S+)', text
        )
        if name_match:
            name = name_match.group(1)
            if name and len(name) <= 6 and name not in ["什么", "啥", "谁", "吗", "是"]:
                self.remember_forever("user_name", name)
                return name
        return user_name

    # ====================================================================
    #  情感（纯规则）
    # ====================================================================

    def _detect_emotion(self, text: str) -> dict:
        """简单情感检测 - 纯规则"""
        t = text.lower()
        if any(w in t for w in ["开心", "高兴", "哈哈", "太好了", "谢谢", "😊", "👍"]):
            return {"dominant_emotion": "happy", "confidence": 0.8}
        if any(w in t for w in ["难过", "伤心", "哭", "难受", "郁闷", "😢"]):
            return {"dominant_emotion": "sad", "confidence": 0.8}
        if any(w in t for w in ["生气", "愤怒", "烦", "讨厌", "滚", "😡"]):
            return {"dominant_emotion": "angry", "confidence": 0.8}
        if any(w in t for w in ["怕", "担心", "紧张", "焦虑", "😰"]):
            return {"dominant_emotion": "fearful", "confidence": 0.7}
        return {"dominant_emotion": "neutral", "confidence": 0.5}

    # ====================================================================
    #  记忆
    # ====================================================================

    def _load_memories(self, session_id: str) -> list:
        try:
            if self.memory:
                return self.memory.get_session_memory(session_id, limit=5)
        except Exception as e:
            print(f"[ChatAgent] 记忆检索失败: {e}")
        return []

    def _save_memory(self, session_id: str, user_input: str, response: str):
        try:
            if self.memory and session_id:
                self.memory.add_session_memory(session_id, user_input, response)
        except Exception as e:
            print(f"[ChatAgent] 保存记忆失败: {e}")

    # ====================================================================
    #  对话
    # ====================================================================

    def _chat(self, user_input: str, original: str, session_id: str,
              emotion: dict, memories: list) -> str:
        """委托给对话引擎"""
        if not self.chat_engine:
            return self._fallback_response(user_input)

        try:
            standard_json = {
                "version": "2.5",
                "session_id": session_id,
                "user_id": self.user_id,
                "raw_input": original,
                "timestamp": datetime.now().isoformat(),
                "action": "chat",
                "target": "text",
                "confidence": 0.85,
                "params": {
                    "context": {
                        "memories": memories,
                        "emotion": emotion,
                        "history": self._history[-6:],
                    }
                },
            }

            result = self.chat_engine.execute(
                message=standard_json, user_id=self.user_id
            )
            response = result.get("output_content", "") or result.get("response", "")
            return response or self._fallback_response(user_input)
        except Exception as e:
            print(f"[ChatAgent] 对话引擎失败: {e}")
            return self._fallback_response(user_input)

    # ====================================================================
    #  历史
    # ====================================================================

    def _update_history(self, user_input: str, response: str):
        self._history.append({
            "user": user_input[:200],
            "assistant": response[:200],
            "timestamp": datetime.now().isoformat()
        })
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    # ====================================================================
    #  辅助
    # ====================================================================

    def _fallback_response(self, user_input: str) -> str:
        return f"您好！我是ClawsJoy助手，有什么可以帮您的吗？"

    def _response(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}

    def get_stats(self) -> Dict:
        return {
            "name": self.name,
            "version": self.version,
            "history_size": len(self._history),
        }


if __name__ == "__main__":
    agent = ChatAgentV4("test")
    print(agent.process("你好", {"session_id": "test"})["response"])
