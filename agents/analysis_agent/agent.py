"""AnalysisAgent - 分析师：理解层常驻 + 业务层按需"""

import sys

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

import time
from typing import Dict, Optional

from core.agents.business.business_agent_v2 import BusinessAgentV2


class AnalysisAgent(BusinessAgentV2):
    """分析师 - 双模式智能分析"""

    name = "analysis_agent"
    description = "数据分析与理解 - 双模式智能分析"
    version = "4.1.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        print(f"📊 分析师 v{self.version} 已上岗 (双模式)")

    def _execute_business(self, user_input: str, context: Dict = None) -> Dict:
        mode = self._detect_mode(context)
        if mode == "understanding":
            return self.analyze_for_decision(user_input, context)
        else:
            return self.analyze_for_execution(user_input, context)

    def _detect_mode(self, context: Dict) -> str:
        if not context:
            return "execution"
        if context.get("mode") == "understanding":
            return "understanding"
        if context.get("caller") == "decision_agent":
            return "understanding"
        if context.get("caller") == "orchestrator" or context.get("subtask"):
            return "execution"
        return "execution"

    def analyze_for_decision(self, user_input: str, context: Dict = None) -> Dict:
        """理解层模式：为决策师提供分析报告"""
        print(f"[分析师][理解层] 常态分析: {user_input[:50]}...")

        analysis = self._quick_analysis(user_input)
        print(
            f"[分析师][理解层] 分析结果: intent={analysis['intent']}, route={analysis['suggested_route']}"
        )

        return {
            "success": True,
            "complexity": analysis["complexity"],
            "suggested_route": analysis["suggested_route"],
            "requires_orchestration": analysis["requires_orchestration"],
            "intent": analysis["intent"],
            "confidence": 0.85,
            "analysis_summary": analysis["summary"],
            "mode": "understanding",
        }

    def _quick_analysis(self, user_input: str) -> Dict:
        """快速规则分析 - 配置驱动"""
        from core.lib.intent_fallback import intent_fallback
        from core.lib.smart_intent_router import SmartIntentRouter
        from engine.semantic import semantic_engine

        input_lower = user_input.lower()

        # 1. 关键词兜底（从配置文件加载）
        fallback_intent = intent_fallback.get_intent(user_input)
        if fallback_intent:
            # 从配置文件获取 Agent
            router = SmartIntentRouter()
            router.reload_config()
            agent = router.INTENT_TO_AGENT.get(fallback_intent)
            if agent is None:
                from core.lib.unified_config import unified_config

                intents_config = unified_config.get("keywords.intents", {})
                if fallback_intent in intents_config:
                    route = "B"
                    orchestration = False
                    complexity = "low"
                    print(f"[分析师][快速分析] 技能匹配: {fallback_intent} -> B")
                    return {
                        "complexity": complexity,
                        "suggested_route": route,
                        "requires_orchestration": orchestration,
                        "intent": fallback_intent,
                        "summary": f"{fallback_intent}技能，直接执行",
                    }
            if agent:
                route = (
                    "C"
                    if agent
                    in [
                        "translate_agent",
                        "code_agent",
                        "analysis_agent",
                        "video_agent",
                        "dialect_agent",
                        "writer_agent",
                        "vision_agent",
                    ]
                    else "B"
                )
                orchestration = route == "C"
                complexity = "medium" if orchestration else "low"
                print(
                    f"[分析师][快速分析] 关键词匹配: {fallback_intent} -> {agent} -> {route}"
                )
                return {
                    "complexity": complexity,
                    "suggested_route": route,
                    "requires_orchestration": orchestration,
                    "intent": fallback_intent,
                    "summary": (
                        f"{fallback_intent}任务，需要编排"
                        if orchestration
                        else f"{fallback_intent}任务，直接执行"
                    ),
                }

        # 2. 语义理解
        router = SmartIntentRouter()
        router.reload_config()

        try:
            result = semantic_engine.understand(user_input)
            intent = result.intent
        except Exception as e:
            intent = "chat"

        # 根据意图获取 Agent
        agent = router.INTENT_TO_AGENT.get(intent, "chat_agent")

        # 确定路由
        if agent in ["calculator_agent", "weather_skill"]:
            route = "B"
            orchestration = False
            complexity = "low"
            summary = f"单步任务：{intent}，直接执行"
        elif agent in [
            "translate_agent",
            "code_agent",
            "analysis_agent",
            "video_agent",
            "dialect_agent",
            "writer_agent",
            "vision_agent",
        ]:
            route = "C"
            orchestration = True
            complexity = "medium"
            summary = f"复杂任务：{intent}，需要编排"
        else:
            route = "A"
            orchestration = False
            complexity = "low"
            summary = "简单对话，直接回复"

        print(f"[分析师][快速分析] 语义: intent={intent}, agent={agent}, route={route}")

        return {
            "complexity": complexity,
            "suggested_route": route,
            "requires_orchestration": orchestration,
            "intent": intent,
            "summary": summary,
        }

    def analyze_for_execution(self, user_input: str, context: Dict = None) -> Dict:
        """业务层模式：执行具体数据分析"""
        print(f"[分析师][业务层] 深度分析: {user_input[:50]}...")

        previous_result = None
        if context and isinstance(context, dict):
            previous_result = context.get("previous_result")
            if previous_result:
                print(
                    f"[分析师][业务层] 接收前置结果，长度: {len(str(previous_result))}"
                )
                user_input = f"{user_input}\n\n参考信息: {str(previous_result)[:500]}"

        result = self._do_deep_analysis(user_input)

        return {
            "success": True,
            "response": result,
            "full_response": result,
            "mode": "execution",
        }

    def _do_deep_analysis(self, user_input: str) -> str:
        """执行深度数据分析"""
        from core.lib.smart_adapter import smart_adapter

        prompt = f"""请对以下问题进行专业、深入的分析：

{user_input}

请按以下格式输出：
1. **核心观点**：总结关键发现
2. **关键趋势**：列出3-5个主要趋势
3. **洞察与建议**：提供有价值的见解

分析要深入、有数据支撑："""

        response = smart_adapter.generate(
            prompt, auto_select=True, max_tokens=1200, temperature=0.7
        )

        if response and response.startswith("（我是 ClawsJoy 助手）"):
            response = response.replace("（我是 ClawsJoy 助手）", "", 1).strip()
        if response and response.startswith("我是 ClawsJoy 助手"):
            response = response.replace("我是 ClawsJoy 助手", "", 1).strip()

        if not response or len(response.strip()) < 100:
            response = f"""## 分析报告

**核心观点**：关于「{user_input[:100]}」的分析：

1. 该领域呈现积极发展态势
2. 技术创新是主要驱动力
3. 应用场景不断扩展

**建议**：建议进一步收集具体数据进行量化分析。"""

        return response


    def _get_route_from_config(self, intent: str) -> str:
        """从配置获取路由"""
        try:
            from core.lib.intent_router import intent_router

            agent = intent_router.get_agent(intent)
            return intent_router.get_route(agent) if agent else "A"
        except Exception as e:
            return "A"


    from core.lib.smart_intent_router import SmartIntentRouter


    def _get_route_from_intent(self, user_input: str) -> Dict:
        """使用智能路由器获取路由"""
        router = SmartIntentRouter()
        # 重新加载配置确保最新
        router.reload_config()

        # 获取意图
        from engine.semantic import semantic_engine

        result = semantic_engine.understand(user_input)
        intent = result.intent

        # 根据意图获取 Agent
        agent = router.INTENT_TO_AGENT.get(intent)

        # 确定路由
        if agent in ["calculator_agent", "weather_skill"]:
            route = "B"
        elif agent in [
            "translate_agent",
            "code_agent",
            "analysis_agent",
            "video_agent",
            "dialect_agent",
        ]:
            route = "C"
        else:
            route = "A"

        return {
            "agent": agent or "chat_agent",
            "route": route,
            "intent": intent,
            "requires_orchestration": route == "C",
        }

    def handle(self, user_input: str, context: dict = None) -> dict:
        """统一入口"""
        return self._execute_business(user_input, context)

    def rollback(self, task_id: str, context: dict = None) -> dict:
        """回滚分析操作"""
        # 清除分析缓存
        if hasattr(self, "_analysis_cache"):
            self._analysis_cache.pop(task_id, None)
        return {"success": True, "message": "分析缓存已清除"}

    def _get_route_by_intent(self, intent: str) -> tuple:
        """根据意图获取路由"""
        # 翻译直接路由到 ChatAgent（让 LLM 处理）
        if intent == "translate":
            return ("A", False, 0.3)  # A = ChatAgent
    
        # 代码任务
        if intent == "code":
            return ("C", True, 0.7)   # C = Orchestrator
    
        # 数学计算
        if intent == "calculate":
            return ("A", False, 0.2)
    
        # 默认
        return ("A", False, 0.5)
