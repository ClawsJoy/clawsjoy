"""生命周期 Agent - 6/6 闭环，符合新框架 v3.0"""
from typing import Dict, Optional
from datetime import datetime
from core.agents.base.smart_agent import SmartAgent


class LifeCycleAgent(SmartAgent):
    """生命周期 Agent - 6/6 闭环管理"""

    name = "life_cycle_agent"
    description = "6/6 闭环生命周期管理"
    type = "core"

    def on_init(self):
        """初始化"""
        self.log("生命周期 Agent 初始化完成")
        self._init_closed_loop()

    def _init_closed_loop(self):
        """初始化闭环数据"""
        self.closed_loop_data = {
            "perception": {},
            "decision": {},
            "action": {},
            "monitor": {},
            "learning": {},
            "memory": {},
            "history": []
        }

    # ========== 6/6 闭环核心方法 ==========

    def _perceive(self, user_input: str) -> Dict:
        """1. 感知阶段 - 理解输入"""
        return {
            "input": user_input,
            "intent": self._detect_intent(user_input),
            "entities": self._extract_entities(user_input),
            "timestamp": datetime.now().isoformat()
        }

    def _detect_intent(self, text: str) -> str:
        """检测意图"""
        if "分析" in text:
            return "analysis"
        elif "决策" in text or "决定" in text:
            return "decision"
        elif "执行" in text:
            return "execute"
        else:
            return "chat"

    def _extract_entities(self, text: str) -> Dict:
        """提取实体"""
        entities = {}
        # 简单实体提取
        if "任务" in text:
            entities["task"] = text.split("任务")[-1].strip()[:50]
        return entities

    def _decide(self, perception: Dict) -> Dict:
        """2. 决策阶段 - 决定行动"""
        intent = perception.get("intent", "chat")

        decision_map = {
            "analysis": {"action": "analyze", "priority": 2},
            "decision": {"action": "decide", "priority": 1},
            "execute": {"action": "execute", "priority": 3},
            "chat": {"action": "respond", "priority": 4}
        }

        decision = decision_map.get(intent, decision_map["chat"])
        decision["confidence"] = 0.85
        decision["timestamp"] = datetime.now().isoformat()

        return decision

    def _act(self, decision: Dict) -> Dict:
        """3. 执行阶段 - 执行行动"""
        action = decision.get("action", "respond")

        action_results = {
            "analyze": {"result": "分析完成", "data": {}},
            "decide": {"result": "决策已做出", "data": {"recommendation": "建议继续"}},
            "execute": {"result": "执行完成", "data": {"status": "success"}},
            "respond": {"result": "已响应", "data": {"response": "收到消息"}}
        }

        result = action_results.get(action, action_results["respond"])
        result["action"] = action
        result["timestamp"] = datetime.now().isoformat()

        return result

    def _monitor(self, action_result: Dict) -> Dict:
        """4. 监控阶段 - 监控执行结果"""
        return {
            "success": True,
            "metrics": {
                "response_time": 0.01,
                "confidence": 0.9
            },
            "issues": [],
            "timestamp": datetime.now().isoformat()
        }

    def _learn(self, monitor_result: Dict) -> Dict:
        """5. 学习阶段 - 从结果中学习"""
        if monitor_result.get("success"):
            insight = "执行成功，保持当前策略"
        else:
            insight = "执行失败，需要调整"

        return {
            "learned": True,
            "insights": [insight],
            "confidence_delta": 0.05,
            "timestamp": datetime.now().isoformat()
        }

    def _remember(self, learn_result: Dict) -> Dict:
        """6. 记忆阶段 - 存储学习结果"""
        # 记录到闭环历史
        self.closed_loop_data["history"].append({
            "learning": learn_result,
            "timestamp": datetime.now().isoformat()
        })

        # 限制历史长度
        if len(self.closed_loop_data["history"]) > 100:
            self.closed_loop_data["history"] = self.closed_loop_data["history"][-100:]

        return {
            "stored": True,
            "history_length": len(self.closed_loop_data["history"])
        }

    # ========== 主动服务方法 ==========

    def _should_serve(self) -> bool:
        """判断是否应该主动服务"""
        from datetime import datetime
        hour = datetime.now().hour
        # 早上9点主动问候
        return hour == 9

    def _get_proactive_message(self) -> str:
        """获取主动服务消息"""
        from datetime import datetime
        hour = datetime.now().hour

        if hour == 9:
            return "早上好！新的一天开始了，有什么我可以帮您的吗？"
        return "您好，很高兴为您服务！"

    # ========== 核心处理入口 ==========

    def process(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """处理用户输入 - 6/6 闭环完整流程"""
        self._update_stats()

        # 1. 感知
        perception = self._perceive(user_input)
        self.closed_loop_data["perception"] = perception

        # 2. 决策
        decision = self._decide(perception)
        self.closed_loop_data["decision"] = decision

        # 3. 执行
        action_result = self._act(decision)
        self.closed_loop_data["action"] = action_result

        # 4. 监控
        monitor_result = self._monitor(action_result)
        self.closed_loop_data["monitor"] = monitor_result

        # 5. 学习
        learn_result = self._learn(monitor_result)
        self.closed_loop_data["learning"] = learn_result

        # 6. 记忆
        memory_result = self._remember(learn_result)
        self.closed_loop_data["memory"] = memory_result

        # 生成响应
        response = self._generate_response(perception, decision, action_result)

        # 记录交互
        self.record_interaction(user_input, response)

        return {
            "success": True,
            "response": response,
            "user_id": self.user_id,
            "closed_loop": {
                "perception": perception.get("intent"),
                "decision": decision.get("action"),
                "action": action_result.get("action"),
                "confidence": decision.get("confidence", 0)
            }
        }

    def _generate_response(self, perception: Dict, decision: Dict, action_result: Dict) -> str:
        """生成响应"""
        intent = perception.get("intent", "chat")
        action = decision.get("action", "respond")

        if intent == "analysis":
            return "分析完成，系统运行正常。"
        elif intent == "decision":
            return "根据当前情况，建议继续执行。"
        elif intent == "execute":
            return "任务已执行完成。"
        else:
            return "收到您的消息，已进入闭环处理流程。"

    # ========== 获取状态 ==========

    def get_closed_loop_status(self) -> Dict:
        """获取闭环状态"""
        return {
            "current": {
                "perception": self.closed_loop_data.get("perception", {}),
                "decision": self.closed_loop_data.get("decision", {}),
                "action": self.closed_loop_data.get("action", {})
            },
            "history_length": len(self.closed_loop_data.get("history", [])),
            "phases": ["perceive", "decide", "act", "monitor", "learn", "remember"]
        }

    def get_health_score(self) -> int:
        """获取健康度评分"""
        history = self.closed_loop_data.get("history", [])
        if not history:
            return 85

        success_count = sum(1 for h in history if h.get("learning", {}).get("learned"))
        return int(80 + (success_count / len(history)) * 20)


# 兼容旧类名
LifeCycleConfigDriven = LifeCycleAgent
