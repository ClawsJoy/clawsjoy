#!/usr/bin/env python3
"""业务基类 - 所有业务 Agent 的基类"""

from abc import abstractmethod
from typing import Any, Callable, Dict, List, Optional

from core.agents.base.smart_agent import SmartAgent


class BusinessAgent(SmartAgent):
    """
    业务智能体基类

    提供通用的业务处理框架:
    1. 预处理 - 安全检查、情感识别
    2. 业务处理 - 子类实现
    3. 后处理 - 审计、记忆、解释
    """

    def handle(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """标准业务处理流程"""

        # 1. 预处理
        pre_result = self._preprocess(user_input, context)
        if not pre_result["success"]:
            return pre_result

        # 2. 业务处理
        try:
            result = self._execute_business(user_input, context)
        except Exception as e:
            result = self._handle_error(e)

        # 3. 后处理
        result = self._postprocess(result, user_input)

        # 4. 审计
        self.audit(
            "business_process",
            {
                "input": user_input[:100],
                "output": result.get("response", "")[:100],
            },
            result=result.get("success", False),
        )

        return result

    def _preprocess(self, user_input: str, context: Dict) -> Dict:
        """预处理"""
        # 安全检查
        if not self.safe_guard(user_input):
            return {"success": False, "response": "操作被安全策略拒绝"}

        # 法律检查
        if not self.legal_check(user_input):
            return {"success": False, "response": "操作违反法律合规要求"}

        # 伦理检查
        ethical_ok, reason = self.ethical_check(user_input)
        if not ethical_ok:
            return {"success": False, "response": reason}

        # 情感识别
        emotion, conf = self.recognize_emotion(user_input)
        self._current_emotion = emotion

        return {"success": True, "emotion": emotion}

    @abstractmethod
    def _execute_business(self, user_input: str, context: Dict) -> Dict:
        """执行业务逻辑（子类实现）"""
        pass

    def _postprocess(self, result: Dict, user_input: str) -> Dict:
        """后处理"""
        # 添加元数据
        result["agent"] = self.name
        result["user_id"] = self.user_id

        # 添加情感回应（如果需要）
        if (
            hasattr(self, "_current_emotion")
            and self._current_emotion.value != "neutral"
        ):
            emotion_response = self.get_emotion_response(self._current_emotion)
            result["emotion_response"] = emotion_response

        return result

    def _handle_error(self, error: Exception) -> Dict:
        """错误处理"""
        self.log(f"业务处理错误: {error}", "ERROR")
        return {
            "success": False,
            "error": str(error),
            "response": f"处理过程中出现问题: {error}",
        }

    def _init_communication(self):
        """初始化通信能力"""
        try:
            from core.lib.agent_communication import AgentCommunication

            self._comm = AgentCommunication()
            self._comm.subscribe(self.name, "task")
            self._comm.subscribe(self.name, "broadcast")
            print(f"📡 [{self.name}] 通信能力已初始化")
        except Exception as e:
            print(f"⚠️ [{self.name}] 通信初始化失败: {e}")

    def send_message(self, to_agent: str, action: str, data: Dict = None) -> str:
        """发送消息到其他 Agent"""
        try:
            return self._comm.send(
                from_agent=self.name,
                to_agent=to_agent,
                payload={"action": action, "data": data or {}},
                msg_type=(
                    MessageType.REQUEST
                    if hasattr(
                        __import__("core.lib.agent_communication"), "MessageType"
                    )
                    else None
                ),
            )
        except Exception as e:
            print(f"[{self.name}] 发送消息失败: {e}")
            return None

    def broadcast(self, event: str, data: Dict = None):
        """广播消息"""
        try:
            self._comm.send_broadcast(
                from_agent=self.name,
                event_type=event,
                payload={"action": event, "data": data or {}},
            )
        except Exception as e:
            print(f"[{self.name}] 广播失败: {e}")

    def get_messages(self, limit: int = 10) -> List[Dict]:
        """获取收到的消息"""
        try:
            return self._comm.get_messages(self.name, limit)
        except:
            return []

    def process(self, user_input: str, context: dict = None) -> dict:
        """统一入口 - 调用 _execute_business"""
        return self._execute_business(user_input, context)
