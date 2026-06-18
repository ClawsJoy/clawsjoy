#!/usr/bin/env python3
"""CommunicableAgent v3.1 - LLM-First 通信基类

增强能力:
1. 😊 情感识别 - 由 LLM 识别用户情绪
2. 🤝 联邦学习 - 跨用户知识共享
3. 📖 可解释性 - 解释决策过程
4. 📋 审计日志 - 记录所有决策
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


class Emotion(Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    SURPRISED = "surprised"
    CONFUSED = "confused"
    NEUTRAL = "neutral"


class DecisionExplanation:
    def __init__(self, decision: str, reasons: List[str], confidence: float):
        self.decision = decision
        self.reasons = reasons
        self.confidence = confidence
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {"decision": self.decision, "reasons": self.reasons, "confidence": self.confidence, "timestamp": self.timestamp}


class CommunicableAgent(BaseAgent):
    """
    LLM-First 通信基类
    """

    VERSION = "3.1.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)

        # ========== 情感识别（由 LLM 驱动）==========
        self._emotion_history: List[Dict] = []
        self._current_emotion = Emotion.NEUTRAL

        # ========== 联邦学习 ==========
        self._federated_knowledge: Dict = {}
        self._local_updates: List[Dict] = []
        self._privacy_threshold = 0.7
        self._knowledge_sharing_enabled = unified_config.get("federated.enabled", True)

        # ========== 可解释性 ==========
        self._decision_history: List[DecisionExplanation] = []
        self._explanation_enabled = unified_config.get("explanation.enabled", True)

        # ========== 审计日志 ==========
        self._audit_log: List[Dict] = []
        self._audit_enabled = unified_config.get("audit.enabled", True)
        self._audit_file = Path("logs/audit") / f"{self.name}_{self.user_id}.json"
        self._audit_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_audit_log()

        print(f"📡 [{self.name}] LLM-First 通信基类初始化完成 v{self.VERSION}")

    # ==================== 情感识别（LLM 驱动）====================

    def recognize_emotion(self, text: str) -> Tuple[Emotion, float]:
        """由 LLM 识别用户情感"""
        prompt = f"""识别以下文本的情感，只输出 JSON。

文本：{text[:200]}

输出格式：{{"emotion": "happy/sad/angry/fearful/surprised/confused/neutral", "confidence": 0.0-1.0, "reason": "简短理由"}}

只输出 JSON：
"""
        try:
            import requests
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2:1.5b-instruct",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 100, "temperature": 0.2}
                },
                timeout=15
            )
            if resp.status_code == 200:
                response = resp.json().get("response", "")
                import re
                match = re.search(r'\{.*\}', response, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                    emotion_str = data.get("emotion", "neutral")
                    confidence = data.get("confidence", 0.5)
                    emotion_map = {
                        "happy": Emotion.HAPPY, "sad": Emotion.SAD, "angry": Emotion.ANGRY,
                        "fearful": Emotion.FEARFUL, "surprised": Emotion.SURPRISED,
                        "confused": Emotion.CONFUSED, "neutral": Emotion.NEUTRAL
                    }
                    emotion = emotion_map.get(emotion_str, Emotion.NEUTRAL)
                    if confidence > 0.3:
                        self._current_emotion = emotion
                    self._emotion_history.append({
                        "text": text[:50], "emotion": emotion.value, "confidence": confidence,
                        "timestamp": datetime.now().isoformat()
                    })
                    if len(self._emotion_history) > 100:
                        self._emotion_history = self._emotion_history[-100:]
                    return emotion, confidence
        except Exception as e:
            print(f"[{self.name}] 情感识别失败: {e}")

        return Emotion.NEUTRAL, 0.5

    def get_emotion_response(self, emotion: Emotion) -> str:
        """由 LLM 生成情感回应"""
        prompt = f"""根据用户情感生成一个自然、友好的回应，简短（1-2句话）。

情感：{emotion.value}

直接输出回应：
"""
        try:
            response = self._call_llm(prompt)
            if response:
                return response.strip()
        except:
            pass

        return "好的，我明白了。"

    def get_emotion_stats(self) -> Dict:
        stats = defaultdict(int)
        for record in self._emotion_history:
            stats[record["emotion"]] += 1
        return {
            "current": self._current_emotion.value,
            "history_count": len(self._emotion_history),
            "distribution": dict(stats),
        }

    def _call_llm(self, prompt: str) -> str:
        try:
            import requests
            resp = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2:1.5b-instruct",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 100, "temperature": 0.7}
                },
                timeout=20
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except:
            pass
        return ""

    # ==================== 联邦学习 ====================

    def share_knowledge(self, knowledge: Dict, privacy_level: float = 0.5) -> bool:
        if not self._knowledge_sharing_enabled or privacy_level < self._privacy_threshold:
            return False

        sanitized = self._sanitize_knowledge(knowledge)
        self.bus_publish("federated.knowledge", {
            "from": self.name, "knowledge": sanitized, "privacy_level": privacy_level,
            "timestamp": datetime.now().isoformat()
        })
        self._local_updates.append({"knowledge": sanitized, "privacy_level": privacy_level, "shared_at": datetime.now().isoformat()})
        return True

    def receive_knowledge(self, knowledge: Dict, from_agent: str) -> bool:
        if not self._knowledge_sharing_enabled or not self._validate_knowledge(knowledge):
            return False

        for key, value in knowledge.items():
            if key not in self._federated_knowledge:
                self._federated_knowledge[key] = []
            self._federated_knowledge[key].append({"value": value, "source": from_agent, "received_at": datetime.now().isoformat()})
        return True

    def _sanitize_knowledge(self, knowledge: Dict) -> Dict:
        sanitized = {}
        sensitive_keys = ["user_id", "password", "token", "email", "phone"]
        for key, value in knowledge.items():
            sanitized[key] = "[REDACTED]" if key in sensitive_keys else value
        return sanitized

    def _validate_knowledge(self, knowledge: Dict) -> bool:
        return bool(knowledge) and len(knowledge) > 0

    def get_federated_stats(self) -> Dict:
        return {
            "enabled": self._knowledge_sharing_enabled,
            "local_updates": len(self._local_updates),
            "received_knowledge": len(self._federated_knowledge),
            "privacy_threshold": self._privacy_threshold,
        }

    # ==================== 可解释性 ====================

    def explain_decision(self, decision: str, reasons: List[str], confidence: float):
        if not self._explanation_enabled:
            return
        self._decision_history.append(DecisionExplanation(decision, reasons, confidence))
        if len(self._decision_history) > 100:
            self._decision_history = self._decision_history[-100:]

    def get_decision_explanation(self, index: int = -1) -> Optional[Dict]:
        if not self._decision_history:
            return None
        if index == -1:
            return self._decision_history[-1].to_dict()
        if 0 <= index < len(self._decision_history):
            return self._decision_history[index].to_dict()
        return None

    def get_all_explanations(self) -> List[Dict]:
        return [exp.to_dict() for exp in self._decision_history]

    # ==================== 审计日志 ====================

    def _load_audit_log(self):
        if self._audit_file.exists():
            try:
                with open(self._audit_file, "r") as f:
                    self._audit_log = json.load(f)
            except:
                self._audit_log = []

    def _save_audit_log(self):
        if not self._audit_enabled:
            return
        try:
            with open(self._audit_file, "w") as f:
                json.dump(self._audit_log, f, indent=2, ensure_ascii=False)
        except:
            pass

    def audit(self, action: str, details: Dict, result: str = "success"):
        if not self._audit_enabled:
            return
        self._audit_log.append({
            "timestamp": datetime.now().isoformat(),
            "agent": self.name, "user_id": self.user_id,
            "action": action, "details": details, "result": result,
            "session_id": self.agent_id
        })
        if len(self._audit_log) > 1000:
            self._audit_log = self._audit_log[-1000:]
        self._save_audit_log()

    def get_audit_log(self, limit: int = 100, action_filter: str = None) -> List[Dict]:
        logs = self._audit_log[-limit:] if limit > 0 else self._audit_log
        if action_filter:
            logs = [log for log in logs if log["action"] == action_filter]
        return logs

    def get_audit_stats(self) -> Dict:
        from collections import Counter
        actions = Counter([log["action"] for log in self._audit_log])
        results = Counter([log["result"] for log in self._audit_log])
        return {
            "total_logs": len(self._audit_log),
            "actions": dict(actions), "results": dict(results),
            "oldest_log": self._audit_log[0]["timestamp"] if self._audit_log else None,
            "newest_log": self._audit_log[-1]["timestamp"] if self._audit_log else None,
        }

    # ==================== 协作决策 ====================

    def collaborative_decision(self, task: str, candidates: List[str]) -> Tuple[str, DecisionExplanation]:
        """由 LLM 辅助协作决策"""
        prompt = f"""根据以下信息，选择最佳 Agent 处理任务。

## 任务
{task}

## 候选 Agent
{json.dumps(candidates, ensure_ascii=False)}

## 输出格式
{{"best_agent": "agent_name", "reason": "选择理由", "confidence": 0.0-1.0}}

只输出 JSON：
"""
        try:
            response = self._call_llm(prompt)
            if response:
                import re
                match = re.search(r'\{.*\}', response, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                    best = data.get("best_agent", candidates[0] if candidates else "")
                    reasons = [data.get("reason", "LLM 评估")]
                    explanation = DecisionExplanation(best, reasons, data.get("confidence", 0.7))
                    self.explain_decision(best, reasons, data.get("confidence", 0.7))
                    self.audit("collaborative_decision", {"task": task, "candidates": candidates}, result=best)
                    return best, explanation
        except:
            pass

        best = candidates[0] if candidates else ""
        explanation = DecisionExplanation(best, ["默认选择"], 0.5)
        return best, explanation

    def get_communication_stats(self) -> Dict:
        return {
            "emotion": self.get_emotion_stats(),
            "federated": self.get_federated_stats(),
            "audit": self.get_audit_stats(),
            "explanations": len(self._decision_history),
        }
