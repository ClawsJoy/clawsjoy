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
        return self.process(user_input, context)

    def process(self, user_input: str, context: Dict = None) -> Dict:
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
        """快速规则分析（不调用 LLM）"""
        input_lower = user_input.lower()
        #  输入: {input_lower[:80]}...")

        # 检测意图
        intent = "general"
        has_analysis = "分析" in input_lower
        has_writing = (
            "写" in input_lower or "总结" in input_lower or "报告" in input_lower
        )
        has_calculation = "计算" in input_lower or any(
            op in input_lower for op in ["加", "减", "乘", "除"]
        )
        has_translation = "翻译" in input_lower
        user_len = len(user_input)

        if has_analysis:
            intent = "analysis"
        if has_writing:
            intent = "writing" if intent == "analysis" else "writing"
        if has_calculation:
            intent = "calculation"
        if has_translation:
            intent = "translation"

        print(
            f"[分析师][快速分析] has_analysis={has_analysis}, has_writing={has_writing}, intent={intent}"
        )

        # 判断复杂度
        if has_analysis and has_writing:
            complexity = "high"
            suggested_route = "C"
            requires_orchestration = True
            summary = "复杂任务：需要分析+写作，建议编排"
            #  匹配: 分析+写作 → C")
        elif has_analysis:
            complexity = "medium"
            suggested_route = "C"
            requires_orchestration = True
            summary = "分析任务：需要深度分析，建议编排"
            #  匹配: 纯分析 → C")
        elif has_calculation:
            complexity = "low"
            suggested_route = "B"
            requires_orchestration = False
            summary = "计算任务，直接执行"
            #  匹配: 计算 → B")
        elif has_translation:
            # 根据长度判断路由
            if user_len > 50:
                complexity = "medium"
                suggested_route = "C"
                requires_orchestration = True
                summary = "长文本翻译任务，需要编排"
                #  匹配: 长翻译 → C")
            else:
                complexity = "low"
                suggested_route = "B"
                requires_orchestration = False
                summary = "短文本翻译，直接执行"
                #  匹配: 短翻译 → B")
        else:
            complexity = "low"
            suggested_route = "A"
            requires_orchestration = False
            summary = "简单对话，直接回复"
            #  匹配: 默认 → A")

        return {
            "complexity": complexity,
            "suggested_route": suggested_route,
            "requires_orchestration": requires_orchestration,
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


analysis_agent = AnalysisAgent()
