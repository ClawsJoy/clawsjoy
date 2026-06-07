# core/lib/chat_engine.py
"""统一对话引擎 - 即插即拔"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import requests
import yaml

from core.orchestration.user_orchestrator import user_orchestrator

logger = logging.getLogger(__name__)


class UnifiedChatEngine:
    """统一对话引擎 - 封装 enhanced_chat 所有逻辑"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.enabled = self.config.get("enabled", True)
        self._init_sub_engines()

        # ========== 在这里添加 ==========
        # 加载长计划配置

        try:
            with open("config/long_plan.yaml", "r") as f:
                self.long_plan_config = yaml.safe_load(f)
        except Exception:
            self.long_plan_config = {
                "min_message_length": 5,
                "action_keywords": [
                    "制作",
                    "创建",
                    "完成",
                    "并且",
                    "同时",
                    "然后",
                    "之后",
                    "接着",
                ],
            }
        # ========== 添加结束 ==========

    def _init_sub_engines(self):
        """初始化子引擎"""
        # 延迟导入，避免循环依赖
        self._emotion_agent = None
        self._security_hooks = None
        self._response_cache = None
        self._atomic_skill_engine = None
        self._semantic_engine = None
        self._decision_agent = None

    def _get_emotion_agent(self):
        if self._emotion_agent is None:
            from core.agents.base.communicable_agent import CommunicableAgent

            self._emotion_agent = CommunicableAgent
        return self._emotion_agent

    def _get_security_hooks(self):
        if self._security_hooks is None:
            from core.lib.security_hooks import SecurityHooks

            self._security_hooks = SecurityHooks
        return self._security_hooks

    def _get_response_cache(self):
        if self._response_cache is None:
            from core.lib.response_cache import response_cache

            self._response_cache = response_cache
        return self._response_cache

    def _get_decision_agent(self):
        if self._decision_agent is None:
            from agents.decision_agent.agent import decision_agent

            self._decision_agent = decision_agent
        return self._decision_agent

    def execute(
        self, message: str, user_id: str = "guest", context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """执行对话处理 - 完整的 enhanced_chat 逻辑"""

        if not self.enabled:
            return {"success": False, "error": "引擎已禁用"}

        context = context or {}
        start_time = datetime.now()

        # ========== 1. 输入处理 ==========
        from engine.security import desensitizer

        message = desensitizer.desensitize(message)

        # 设置用户上下文
        from core.lib.user_context import user_context

        with user_context(user_id):
            emotion, emotion_conf = self._recognize_emotion(message, user_id)

        # ========== 2. 安全钩子检查 ==========
        security_result = self._check_security(message, user_id)
        if security_result:
            return security_result

        # ========== 3. 长计划判断（优先） ==========
        long_plan_result = self._check_long_plan(message, user_id)
        if long_plan_result:
            return long_plan_result

        # ========== 4. 缓存检查 ==========
        cached_result = self._check_cache(user_id, message, emotion, emotion_conf)
        if cached_result:
            return cached_result

        # ========== 5. 决策路由（核心） ==========
        route_result = self._route_by_decision_agent(
            message, user_id, emotion, emotion_conf
        )
        if route_result:
            return route_result

        # ========== 6. 原子技能和话本匹配 ==========
        atomic_result = self._match_atomic_skill(
            message, user_id, emotion, emotion_conf
        )
        if atomic_result:
            return atomic_result

        # ========== 7. 状态回答 ==========
        state_result = self._answer_from_state(message, user_id, emotion, emotion_conf)
        if state_result:
            return state_result

        # ========== 8. LLM 兜底 ==========
        return self._llm_fallback(message, user_id, emotion, emotion_conf)

    def _recognize_emotion(self, message: str, user_id: str):
        """情感识别"""
        try:
            AgentClass = self._get_emotion_agent()
            temp_agent = AgentClass(user_id)
            emotion, emotion_conf = temp_agent.recognize_emotion(message)
            return emotion, emotion_conf
        except Exception as e:
            logger.warning(f"情感识别失败: {e}")
            return "neutral", 0.5

    def _check_security(self, message: str, user_id: str) -> Optional[Dict]:
        """安全检查"""
        SecurityHooks = self._get_security_hooks()

        # 输入清洗
        ok, cleaned = True, message

        # 危险模式检测
        ok, error_msg = SecurityHooks.check_dangerous_patterns(message)
        if not ok:
            return {
                "success": False,
                "error": error_msg,
                "response": f"⚠ 检测到危险操作: {error_msg}",
                "enhanced": True,
                "user_id": user_id,
            }

        # 频率限制
        ok, error_msg = SecurityHooks.check_rate_limit(
            user_id, {"max_requests_per_minute": 30}
        )
        if not ok:
            return {
                "success": False,
                "error": error_msg,
                "response": error_msg,
                "enhanced": True,
                "user_id": user_id,
            }
        return None

    def _check_long_plan(self, message: str, user_id: str) -> Optional[Dict]:
        """长计划判断"""

        logger.debug(f" user_orchestrator id: {id(user_orchestrator)}")
        logger.debug(f" user_id: {user_id}, message: {message}")

        # 1. 先检查是否有等待确认的计划
        pending = user_orchestrator.get_pending_plan_by_user(user_id)
        logger.debug(f" pending={pending}")
        # 2. 如果有等待确认的计划，且用户回复了确认指令
        if pending and message in ["开始", "确认", "好的", "可以", "执行", "嗯", "是"]:
            result = user_orchestrator.confirm_by_user(message, user_id)
            if result and result.get("success"):
                return result
            return {
                "success": False,
                "response": "确认失败，请重试",
                "agent": "orchestrator",
                "user_id": user_id,
            }

        # 3. 判断是否是新的长计划
        if self._is_long_plan(message):
            try:
                logger.debug(f" user_id: {user_id}, message: {message}")
                result = user_orchestrator.start(message, user_id)
                if result and result.get("success"):
                    return result
                return {
                    "success": True,
                    "response": "任务已开始执行",
                    "agent": "orchestrator",
                    "orchestrated": True,
                    "user_id": user_id,
                }
            except Exception as e:
                logger.error(f"长计划执行失败: {e}", exc_info=True)
                return {
                    "success": False,
                    "error": str(e),
                    "response": f"任务执行失败: {e}",
                    "agent": "orchestrator",
                    "user_id": user_id,
                }
        return None

    def _is_long_plan(self, message: str) -> bool:
        """判断是否长计划"""
        min_len = self.long_plan_config.get("min_message_length", 5)
        if len(message) < min_len:
            return False

        action_keywords = self.long_plan_config.get(
            "action_keywords",
            ["制作", "创建", "完成", "并且", "同时", "然后", "之后", "接着"],
        )
        count = sum(1 for kw in action_keywords if kw in message)
        return count >= 2 or ("视频" in message and "制作" in message)

    def _check_cache(
        self, user_id: str, message: str, emotion, emotion_conf
    ) -> Optional[Dict]:
        """检查缓存"""
        cache = self._get_response_cache()
        cached = cache.get(user_id, message)
        if cached:
            return {
                "success": True,
                "response": cached,
                "cached": True,
                "agent": "cached",
                "enhanced": True,
                "user_id": user_id,
                "detected_emotion": self._get_emotion_value(emotion),
                "emotion_confidence": emotion_conf,
            }
        return None

    def _route_by_decision_agent(
        self, message: str, user_id: str, emotion, emotion_conf
    ) -> Optional[Dict]:
        """决策Agent路由"""
        try:
            decision_agent = self._get_decision_agent()
            result = decision_agent.process(message, {"user_id": user_id})

            response = result.get("response", "处理完成")
            agent_name = result.get("agent", "decision_agent")

            self._save_memory(user_id, f"用户说: {message}")
            self._save_memory(user_id, f"{agent_name}说: {response[:200]}")
            self._record_learning(f"{user_id} -> {agent_name}", True)

            cache = self._get_response_cache()
            cache.set(user_id, message, response)

            return {
                "success": True,
                "response": response,
                "agent": agent_name,
                "routed": True,
                "enhanced": True,
                "user_id": user_id,
                "detected_emotion": self._get_emotion_value(emotion),
                "emotion_confidence": emotion_conf,
            }
        except Exception as e:
            logger.warning(f"决策路由失败: {e}")
            return None

    def _match_atomic_skill(
        self, message: str, user_id: str, emotion, emotion_conf
    ) -> Optional[Dict]:
        """原子技能匹配"""
        try:
            from agents.chat_agent import ChatAgent

            chat_agent = ChatAgent(user_id=user_id)

            atomic_result = chat_agent._check_atomic_skill(message)
            if atomic_result:
                self._save_memory(user_id, f"用户说: {message}")
                self._save_memory(user_id, f"ClawsJoy说: {atomic_result[:200]}")
                cache = self._get_response_cache()
                cache.set(user_id, message, atomic_result)
                return {
                    "success": True,
                    "response": atomic_result,
                    "agent": "atomic_skill",
                    "enhanced": True,
                    "user_id": user_id,
                    "detected_emotion": self._get_emotion_value(emotion),
                    "emotion_confidence": emotion_conf,
                }

            intent = chat_agent._match_intent(message)
            if intent:
                template = chat_agent._get_template(intent)
                if template:
                    self._save_memory(user_id, f"用户说: {message}")
                    self._save_memory(user_id, f"ClawsJoy说: {template[:200]}")
                    cache = self._get_response_cache()
                    cache.set(user_id, message, template)
                    return {
                        "success": True,
                        "response": template,
                        "agent": "scriptbook",
                        "enhanced": True,
                        "user_id": user_id,
                        "detected_emotion": self._get_emotion_value(emotion),
                        "emotion_confidence": emotion_conf,
                    }
        except Exception as e:
            logger.warning(f"原子技能匹配失败: {e}")
        return None

    def _answer_from_state(
        self, message: str, user_id: str, emotion, emotion_conf
    ) -> Optional[Dict]:
        """从状态回答"""
        try:
            direct_answer = self._get_state_answer(message, user_id)
            if direct_answer:
                cache = self._get_response_cache()
                cache.set(user_id, message, direct_answer)
                return {
                    "success": True,
                    "response": direct_answer,
                    "agent": "state_manager",
                    "enhanced": True,
                    "user_id": user_id,
                    "detected_emotion": self._get_emotion_value(emotion),
                    "emotion_confidence": emotion_conf,
                }
        except Exception as e:
            logger.warning(f"状态回答失败: {e}")
        return None

    def _llm_fallback(self, message: str, user_id: str, emotion, emotion_conf) -> Dict:
        """LLM兜底"""
        try:
            from core.lib.config import config

            resp = requests.post(
                f"{config.LLM_URL}/chat", json={"message": message}, timeout=60
            )
            if resp.status_code == 200:
                response = resp.json().get("response", "")
            else:
                response = f"服务异常: {resp.status_code}"
        except Exception as e:
            response = f"服务繁忙: {e}"

        self._save_memory(user_id, f"用户说: {message}")
        self._save_memory(user_id, f"ClawsJoy说: {response[:200]}")
        self._record_learning(f"对话: {user_id} -> {message[:30]}", True)

        cache = self._get_response_cache()
        cache.set(user_id, message, response)

        return {
            "success": True,
            "response": response,
            "agent": "chat_agent",
            "enhanced": True,
            "user_id": user_id,
            "detected_emotion": self._get_emotion_value(emotion),
            "emotion_confidence": emotion_conf,
        }

    def _save_memory(self, user_id: str, content: str):
        """保存记忆"""
        try:
            from core.lib.memory import save_memory

            save_memory(user_id, content)
        except Exception as e:
            logger.debug(f"记忆保存失败: {e}")

    def _record_learning(self, key: str, value: bool):
        """记录学习"""
        try:
            from core.lib.learning import record_learning

            record_learning(key, value)
        except Exception as e:
            logger.debug(f"学习记录失败: {e}")

    def _get_state_answer(self, message: str, user_id: str) -> Optional[str]:
        """获取状态回答"""
        # 实现原有的 answer_from_state 逻辑
        return None

    def _get_emotion_value(self, emotion):
        """获取情感值"""
        if hasattr(emotion, "value"):
            return emotion.value
        return str(emotion) if emotion else "neutral"

    def get_status(self) -> Dict:
        """获取引擎状态"""
        return {
            "name": "UnifiedChatEngine",
            "enabled": self.enabled,
            "version": "1.0.0",
        }

    def update_config(self, config: Dict):
        """更新配置"""
        self.config.update(config)
        self.enabled = self.config.get("enabled", True)
        logger.info(f"📋 对话引擎配置已更新: enabled={self.enabled}")


# 全局单例
chat_engine = UnifiedChatEngine()
