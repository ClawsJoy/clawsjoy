#!/usr/bin/env python3
"""CommunicableAgent v3.0 - 增强通信能力

新增能力:
1. 😊 情感识别 - 识别用户情绪并适当回应
2. 🤝 联邦学习 - 跨用户知识共享（隐私保护）
3. 📖 可解释性 - 解释决策过程
4. 📋 审计日志 - 记录所有决策用于合规
"""

import hashlib
import json
import time
from collections import defaultdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from core.agents.base.base_agent import BaseAgent
from core.lib.unified_config import unified_config


# ========== 情感类型 ==========
class Emotion(Enum):
    """情感类型"""

    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    SURPRISED = "surprised"
    CONFUSED = "confused"
    NEUTRAL = "neutral"


# ========== 决策可解释性 ==========
class DecisionExplanation:
    """决策解释"""

    def __init__(self, decision: str, reasons: List[str], confidence: float):
        self.decision = decision
        self.reasons = reasons
        self.confidence = confidence
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {
            "decision": self.decision,
            "reasons": self.reasons,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
        }


# ========== 增强通信基类 ==========
class CommunicableAgent(BaseAgent):
    """
    增强通信基类 - 支持情感识别、联邦学习、可解释性、审计日志
    """

    VERSION = "3.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)

        # ========== 😊 情感识别 ==========
        self._emotion_patterns = self._init_emotion_patterns()
        self._emotion_history: List[Dict] = []  # 情感历史
        self._current_emotion = Emotion.NEUTRAL

        # ========== 🤝 联邦学习 ==========
        self._federated_knowledge: Dict = {}  # 共享知识
        self._local_updates: List[Dict] = []  # 本地更新
        self._privacy_threshold = 0.7  # 隐私阈值，低于此值不共享
        self._knowledge_sharing_enabled = unified_config.get("federated.enabled", True)

        # ========== 📖 可解释性 ==========
        self._decision_history: List[DecisionExplanation] = []
        self._explanation_enabled = unified_config.get("explanation.enabled", True)

        # ========== 📋 审计日志 ==========
        self._audit_log: List[Dict] = []
        self._audit_enabled = unified_config.get("audit.enabled", True)
        self._audit_file = Path("logs/audit") / f"{self.name}_{self.user_id}.json"
        self._audit_file.parent.mkdir(parents=True, exist_ok=True)

        # 加载历史审计日志
        self._load_audit_log()

        print(f"📡 [{self.name}] 通信能力初始化完成 v{self.VERSION}")
        print(f"   😊 情感识别: 已启用")
        print(
            f"   🤝 联邦学习: {'已启用' if self._knowledge_sharing_enabled else '已禁用'}"
        )
        print(f"   📖 可解释性: {'已启用' if self._explanation_enabled else '已禁用'}")
        print(f"   📋 审计日志: {'已启用' if self._audit_enabled else '已禁用'}")

    # ==================== 😊 情感识别 ====================

    def _init_emotion_patterns(self) -> Dict:
        """初始化情感识别模式"""
        return {
            Emotion.HAPPY: {
                "keywords": [
                    "开心",
                    "高兴",
                    "太好了",
                    "nice",
                    "great",
                    "awesome",
                    "哈哈",
                    "😊",
                    "🎉",
                ],
                "response_templates": [
                    "很高兴您心情不错！😊",
                    "您的开心感染了我！",
                    "太好了，能帮到您我很开心！",
                ],
            },
            Emotion.SAD: {
                "keywords": ["难过", "伤心", "沮丧", "sad", "失望", "😢", "😭"],
                "response_templates": [
                    "很抱歉听到这个消息...有什么我可以帮您的吗？",
                    "我理解您的感受，希望您能好起来。",
                    "如果需要倾诉，我随时在这里。",
                ],
            },
            Emotion.ANGRY: {
                "keywords": ["生气", "愤怒", "恼火", "angry", "😠", "🤬"],
                "response_templates": [
                    "很抱歉让您感到不满，我会努力改进。",
                    "我理解您的情绪，请问具体是什么问题？",
                    "请告诉我哪里做得不好，我会立即改进。",
                ],
            },
            Emotion.CONFUSED: {
                "keywords": ["不明白", "不懂", "confused", "什么意思", "😕", "🤔"],
                "response_templates": [
                    "让我重新解释一下...",
                    "抱歉没说清楚，我换个方式说明：",
                    "您能具体说一下哪里不明白吗？",
                ],
            },
            Emotion.SURPRISED: {
                "keywords": ["惊讶", "没想到", "surprised", "哇", "😲", "😮"],
                "response_templates": [
                    "是的，没想到吧！",
                    "这就是我能做到的！",
                    "惊喜吗？还有更多呢！",
                ],
            },
        }

    def recognize_emotion(self, text: str) -> Tuple[Emotion, float]:
        """
        识别用户情感
        返回: (情感类型, 置信度)
        """
        text_lower = text.lower()
        best_emotion = Emotion.NEUTRAL
        best_score = 0.0

        for emotion, patterns in self._emotion_patterns.items():
            score = 0
            for keyword in patterns["keywords"]:
                if keyword in text_lower:
                    score += 1

            # 表情符号权重更高
            for keyword in patterns["keywords"]:
                if keyword in text:
                    score += 2

            if score > best_score:
                best_score = score
                best_emotion = emotion

        # 归一化置信度（简单处理）
        confidence = min(best_score / 5, 1.0) if best_score > 0 else 0.5

        # 更新当前情感
        if confidence > 0.3:
            self._current_emotion = best_emotion

        # 记录情感历史
        self._emotion_history.append(
            {
                "text": text[:50],
                "emotion": best_emotion.value,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # 保留最近100条
        if len(self._emotion_history) > 100:
            self._emotion_history = self._emotion_history[-100:]

        return best_emotion, confidence

    def get_emotion_response(self, emotion: Emotion) -> str:
        """根据情感生成适当回应"""
        patterns = self._emotion_patterns.get(
            emotion, self._emotion_patterns[Emotion.NEUTRAL]
        )
        import random

        return random.choice(patterns["response_templates"])

    def get_emotion_stats(self) -> Dict:
        """获取情感统计"""
        stats = defaultdict(int)
        for record in self._emotion_history:
            stats[record["emotion"]] += 1
        return {
            "current": self._current_emotion.value,
            "history_count": len(self._emotion_history),
            "distribution": dict(stats),
        }

    # ==================== 🤝 联邦学习 ====================

    def share_knowledge(self, knowledge: Dict, privacy_level: float = 0.5) -> bool:
        """
        分享知识到联邦学习网络
        privacy_level: 0-1, 越高越保护隐私
        """
        if not self._knowledge_sharing_enabled:
            return False

        # 隐私保护：低于阈值不分享
        if privacy_level < self._privacy_threshold:
            print(
                f"🔒 [{self.name}] 知识隐私级别 {privacy_level} 低于阈值 {self._privacy_threshold}，不分享"
            )
            return False

        # 脱敏处理
        sanitized = self._sanitize_knowledge(knowledge)

        # 广播到其他 Agent
        self.bus_publish(
            "federated.knowledge",
            {
                "from": self.name,
                "knowledge": sanitized,
                "privacy_level": privacy_level,
                "timestamp": datetime.now().isoformat(),
            },
        )

        # 记录本地更新
        self._local_updates.append(
            {
                "knowledge": sanitized,
                "privacy_level": privacy_level,
                "shared_at": datetime.now().isoformat(),
            }
        )

        print(f"🤝 [{self.name}] 已分享知识到联邦网络")
        return True

    def receive_knowledge(self, knowledge: Dict, from_agent: str) -> bool:
        """接收联邦学习知识"""
        if not self._knowledge_sharing_enabled:
            return False

        # 验证知识有效性
        if not self._validate_knowledge(knowledge):
            return False

        # 合并到本地知识库
        for key, value in knowledge.items():
            if key not in self._federated_knowledge:
                self._federated_knowledge[key] = []
            self._federated_knowledge[key].append(
                {
                    "value": value,
                    "source": from_agent,
                    "received_at": datetime.now().isoformat(),
                }
            )

        print(f"📚 [{self.name}] 从 {from_agent} 接收到联邦知识")
        return True

    def _sanitize_knowledge(self, knowledge: Dict) -> Dict:
        """知识脱敏 - 移除个人身份信息"""
        sanitized = {}
        sensitive_keys = ["user_id", "password", "token", "email", "phone"]

        for key, value in knowledge.items():
            if key not in sensitive_keys:
                sanitized[key] = value
            else:
                sanitized[key] = "[REDACTED]"

        return sanitized

    def _validate_knowledge(self, knowledge: Dict) -> bool:
        """验证知识有效性"""
        # 简单验证：非空且有内容
        return bool(knowledge) and len(knowledge) > 0

    def get_federated_stats(self) -> Dict:
        """获取联邦学习统计"""
        return {
            "enabled": self._knowledge_sharing_enabled,
            "local_updates": len(self._local_updates),
            "received_knowledge": len(self._federated_knowledge),
            "privacy_threshold": self._privacy_threshold,
        }

    # ==================== 📖 可解释性 ====================

    def explain_decision(self, decision: str, reasons: List[str], confidence: float):
        """记录决策解释"""
        if not self._explanation_enabled:
            return

        explanation = DecisionExplanation(decision, reasons, confidence)
        self._decision_history.append(explanation)

        # 保留最近100条
        if len(self._decision_history) > 100:
            self._decision_history = self._decision_history[-100:]

    def get_decision_explanation(self, index: int = -1) -> Optional[Dict]:
        """获取决策解释"""
        if not self._decision_history:
            return None

        if index == -1:
            return self._decision_history[-1].to_dict()

        if 0 <= index < len(self._decision_history):
            return self._decision_history[index].to_dict()

        return None

    def get_all_explanations(self) -> List[Dict]:
        """获取所有决策解释"""
        return [exp.to_dict() for exp in self._decision_history]

    # ==================== 📋 审计日志 ====================

    def _load_audit_log(self):
        """加载审计日志"""
        if self._audit_file.exists():
            try:
                with open(self._audit_file, "r") as f:
                    self._audit_log = json.load(f)
                print(f"   📋 已加载 {len(self._audit_log)} 条审计日志")
            except Exception as e:
                print(f"   ⚠️ 加载审计日志失败: {e}")
                self._audit_log = []

    def _save_audit_log(self):
        """保存审计日志"""
        if not self._audit_enabled:
            return

        try:
            with open(self._audit_file, "w") as f:
                json.dump(self._audit_log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ 保存审计日志失败: {e}")

    def audit(self, action: str, details: Dict, result: str = "success"):
        """
        记录审计日志
        用于合规、追溯、分析
        """
        if not self._audit_enabled:
            return

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "user_id": self.user_id,
            "action": action,
            "details": details,
            "result": result,
            "session_id": self.agent_id,
        }

        self._audit_log.append(log_entry)

        # 保留最近1000条
        if len(self._audit_log) > 1000:
            self._audit_log = self._audit_log[-1000:]

        self._save_audit_log()

    def get_audit_log(self, limit: int = 100, action_filter: str = None) -> List[Dict]:
        """获取审计日志"""
        logs = self._audit_log[-limit:] if limit > 0 else self._audit_log

        if action_filter:
            logs = [log for log in logs if log["action"] == action_filter]

        return logs

    def get_audit_stats(self) -> Dict:
        """获取审计统计"""
        from collections import Counter

        actions = Counter([log["action"] for log in self._audit_log])
        results = Counter([log["result"] for log in self._audit_log])

        return {
            "total_logs": len(self._audit_log),
            "actions": dict(actions),
            "results": dict(results),
            "oldest_log": self._audit_log[0]["timestamp"] if self._audit_log else None,
            "newest_log": self._audit_log[-1]["timestamp"] if self._audit_log else None,
        }

    # ==================== 增强通信方法 ====================

    def send_with_emotion(
        self, target: str, message: str, emotion: Emotion = None
    ) -> bool:
        """带情感的通信"""
        if emotion is None:
            emotion = self._current_emotion

        payload = {
            "from": self.name,
            "to": target,
            "message": message,
            "emotion": emotion.value,
            "timestamp": datetime.now().isoformat(),
        }

        # 审计记录
        self.audit("send_message", {"target": target, "message_length": len(message)})

        return self.bus_publish(f"agent.{target}.message", payload)

    def collaborative_decision(
        self, task: str, candidates: List[str]
    ) -> Tuple[str, DecisionExplanation]:
        """
        协作决策 - 多个 Agent 共同决策
        返回: (决策结果, 解释)
        """
        # 收集各 Agent 的意见
        opinions = []
        for candidate in candidates:
            if candidate == self.name:
                # 自己的意见
                can = self.can_handle(task)
                opinions.append(
                    {
                        "agent": candidate,
                        "can": can.get("can", False),
                        "confidence": can.get("confidence", 0),
                        "reason": can.get("reason", ""),
                    }
                )
            else:
                # 请求其他 Agent 的意见
                response = self.http_call(candidate, f"can_handle:{task}")
                if response and "error" not in response:
                    opinions.append(
                        {
                            "agent": candidate,
                            "can": response.get("can", False),
                            "confidence": response.get("confidence", 0),
                            "reason": response.get("reason", ""),
                        }
                    )

        # 选择最佳 Agent
        best = max(opinions, key=lambda x: x["confidence"] if x["can"] else -1)

        # 生成解释
        reasons = [
            f"候选 Agent: {', '.join([o['agent'] for o in opinions])}",
            f"最佳选择: {best['agent']} (置信度 {best['confidence']:.0%})",
            f"理由: {best['reason']}",
        ]

        explanation = DecisionExplanation(best["agent"], reasons, best["confidence"])
        self.explain_decision(best["agent"], reasons, best["confidence"])

        # 审计记录
        self.audit(
            "collaborative_decision",
            {"task": task, "candidates": candidates},
            result=best["agent"],
        )

        return best["agent"], explanation

    # ==================== 重写父类方法 ====================

    def process(self, user_input: str, context: Dict = None) -> Dict:
        """
        重写 process 方法，集成情感识别和审计
        """
        # 1. 情感识别
        emotion, confidence = self.recognize_emotion(user_input)

        # 2. 安全检查
        if not self.safe_guard(user_input, context):
            self.audit("process", {"input": user_input[:50]}, result="rejected_safety")
            return {
                "success": False,
                "error": "操作被安全策略拒绝",
                "response": "抱歉，我无法执行这个操作，因为它可能不安全。",
            }

        # 3. 法律检查
        if not self.legal_check(user_input):
            self.audit("process", {"input": user_input[:50]}, result="rejected_legal")
            return {
                "success": False,
                "error": "操作违反法律合规要求",
                "response": "抱歉，我无法执行这个操作，因为它可能违反法律法规。",
            }

        # 4. 伦理检查
        ethical_ok, reason = self.ethical_check(user_input)
        if not ethical_ok:
            self.audit(
                "process",
                {"input": user_input[:50], "reason": reason},
                result="rejected_ethical",
            )
            return {
                "success": False,
                "error": reason,
                "response": f"抱歉，{reason}。",
            }

        # 5. 更新统计
        self._stats["total_interactions"] += 1
        self.last_active = datetime.now()

        # 6. 执行实际处理（子类实现）
        result = (
            super().process(user_input, context) if hasattr(super(), "process") else {}
        )

        # 7. 根据情感调整响应（如果需要）
        if emotion != Emotion.NEUTRAL and confidence > 0.6:
            emotion_response = self.get_emotion_response(emotion)
            result["emotion_response"] = emotion_response
            result["detected_emotion"] = emotion.value

        # 8. 审计记录
        self.audit(
            "process",
            {
                "input": user_input[:100],
                "emotion": emotion.value,
                "emotion_confidence": confidence,
            },
            result=result.get("success", "unknown"),
        )

        # 9. 记录到会话记忆
        self._session_memory[user_input[:50]] = result.get("response", "")[:100]

        return result

    # ==================== 统计报告 ====================

    def get_communication_stats(self) -> Dict:
        """获取通信统计"""
        return {
            "emotion": self.get_emotion_stats(),
            "federated": self.get_federated_stats(),
            "audit": self.get_audit_stats(),
            "explanations": len(self._decision_history),
        }
