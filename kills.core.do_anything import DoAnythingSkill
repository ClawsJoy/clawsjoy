#!/usr/bin/env python3
"""大脑调度器 v5.1.0 - 配置驱动路由器（优化版）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from core.lib.unified_config import unified_config


class DoAnythingSkill:
    """
    大脑调度器 - 配置驱动路由器
    
    职责：根据 brain_rules.yaml 将任务路由到对应执行器
    支持：数学计算、规则路由、多引擎智能路由、LLM 兜底
    """

    name = "do_anything"
    description = "智能大脑：配置驱动的任务路由"
    version = "5.1.0"
    category = "orchestrator"

    def __init__(self):
        self._load_config()
        self._load_executors()
        print(f"🧠 DoAnything v{self.version} 启动")

    # ================================================================
    #  配置加载
    # ================================================================

    def _load_config(self):
        """加载路由配置"""
        config_file = Path("config/brain_rules.yaml")
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    self.config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"⚠️ 加载配置失败: {e}")
                self.config = {}
        else:
            self.config = {}

        self.priority = self.config.get("priority", [])
        self.executors_config = self.config.get("executors", {})
        print(f"📋 加载 {len(self.priority)} 条路由规则")

    def _load_executors(self):
        """加载执行器"""
        self.executors = {}

        for name, exec_config in self.executors_config.items():
            if not exec_config.get("enabled", True):
                continue

            module_path = exec_config.get("module")
            if not module_path:
                continue

            try:
                module = __import__(module_path, fromlist=[''])
                executor_name = exec_config.get("class", name)

                if hasattr(module, executor_name):
                    self.executors[name] = getattr(module, executor_name)
                elif hasattr(module, name):
                    self.executors[name] = getattr(module, name)
                else:
                    self.executors[name] = module

                print(f"✅ 加载执行器: {name}")
            except Exception as e:
                print(f"⚠️ 加载执行器 {name} 失败: {e}")

        # 确保有 LLM 执行器
        if "llm_executor" not in self.executors:
            self.executors["llm_executor"] = self._llm_executor

    # ================================================================
    #  核心执行
    # ================================================================

    def execute(self, params: Dict) -> Dict:
        """执行路由"""
        # 兼容多种输入格式
        goal = params.get("goal") or params.get("input") or params.get("query") or params.get("text")
        if isinstance(params, str):
            goal = params
        if not goal:
            return {"success": False, "error": "需要提供目标", "result": "请提供 goal 参数"}

        print(f"🧠 [大脑] 收到任务: {goal[:100]}")

        # 1. 快速数学计算
        math_result = self._try_math(goal)
        if math_result:
            return math_result

        # 2. 规则路由
        for rule in self.priority:
            handler_name = rule.get("handler")
            if not handler_name:
                continue

            if not self._match_rule(goal, rule):
                continue

            executor = self.executors.get(handler_name)
            if not executor:
                print(f"⚠️ 执行器未找到: {handler_name}")
                continue

            try:
                if hasattr(executor, 'execute'):
                    result = executor.execute(goal, {"goal": goal})
                elif callable(executor):
                    result = executor(goal, {"goal": goal})
                else:
                    continue

                if result and result.get("success"):
                    return self._format_response(result, rule.get("name", handler_name), goal)
            except Exception as e:
                print(f"⚠️ 执行器 {handler_name} 异常: {e}")
                continue

        # 3. 兜底：多引擎智能路由
        return self._smart_route(goal)

    # ================================================================
    #  规则匹配
    # ================================================================

    def _match_rule(self, goal: str, rule: dict) -> bool:
        """检查规则是否匹配"""
        # 关键词匹配
        keywords = rule.get("keywords", [])
        if keywords:
            for keyword in keywords:
                if keyword in goal:
                    return True
            return False

        # 正则匹配
        pattern = rule.get("pattern")
        if pattern:
            if re.search(pattern, goal):
                return True

        # 默认规则
        return rule.get("default", False)

    # ================================================================
    #  快速数学计算
    # ================================================================

    def _try_math(self, goal: str) -> Optional[Dict]:
        """尝试数学计算"""
        match = re.search(r'(\d+)\s*([+\-*/xX])\s*(\d+)', goal)
        if not match:
            return None

        try:
            a = int(match.group(1))
            op = match.group(2)
            b = int(match.group(3))

            if op in ['x', 'X']:
                op = '*'

            result = eval(f"{a}{op}{b}")
            return self._format_response(
                {"success": True, "result": result, "response": f"{a} {op} {b} = {result}"},
                "math", goal
            )
        except Exception:
            return None

    # ================================================================
    #  多引擎智能路由（兜底）
    # ================================================================

    def _smart_route(self, goal: str) -> Dict:
        """智能路由 - 多引擎集成"""
        try:
            # 1. 语义理解
            semantic = self._call_semantic(goal)

            # 2. 知识检索
            knowledge = self._search_knowledge(goal)

            # 3. 逻辑推理
            reasoning = self._reason(goal)

            # 4. LLM 生成
            if self.executors.get("llm_executor"):
                result = self.executors["llm_executor"].execute(goal, {"goal": goal})
                if result and result.get("success"):
                    return self._format_response(result, "llm", goal)

            # 5. 综合响应
            response = self._build_smart_response(goal, semantic, knowledge, reasoning)
            return self._format_response(
                {"success": True, "result": response, "response": response},
                "smart_route", goal
            )

        except Exception as e:
            return self._format_response(
                {"success": False, "error": str(e), "result": f"处理失败: {e}"},
                "error", goal
            )

    def _call_semantic(self, goal: str) -> Dict:
        """调用语义引擎"""
        try:
            from engine.semantic import semantic_engine
            result = semantic_engine.understand(goal)
            return {"intent": result.intent, "confidence": result.confidence}
        except Exception as e:
            print(f"语义引擎失败: {e}")
            return {"intent": "unknown", "confidence": 0.0}

    def _search_knowledge(self, goal: str) -> str:
        """搜索知识库"""
        try:
            from engine.knowledge import knowledge_engine
            results = knowledge_engine.query(goal)
            if results:
                return results[0].get("content", "")[:300]
        except Exception:
            pass
        return ""

    def _reason(self, goal: str) -> Dict:
        """逻辑推理"""
        try:
            from engine.reasoning import reasoning_engine
            decision, confidence, reasoning = reasoning_engine.process(goal)
            return {"decision": decision, "confidence": confidence, "reasoning": reasoning}
        except Exception:
            return {}

    def _build_smart_response(self, goal: str, semantic: Dict, knowledge: str, reasoning: Dict) -> str:
        """构建智能响应"""
        lines = [f"收到：{goal}"]
        if semantic.get("intent"):
            lines.append(f"意图：{semantic['intent']}")
        if knowledge:
            lines.append(f"相关知识：{knowledge[:100]}...")
        if reasoning.get("reasoning"):
            lines.append(f"推理：{reasoning['reasoning'][:100]}...")
        return "\n".join(lines)

    # ================================================================
    #  LLM 执行器（内置兜底）
    # ================================================================

    def _llm_executor(self, goal: str, params: Dict) -> Dict:
        """LLM 执行器"""
        try:
            from core.agents.wisdom.wisdom_factory import wisdom_factory
            agent = wisdom_factory.get_wisdom_agent("chat_agent", "default")
            if agent:
                result = agent.process(goal)
                return {"success": True, "result": result.get("response", "完成")}
            return {"success": False, "error": "LLM Agent 不可用"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ================================================================
    #  响应格式化
    # ================================================================

    def _format_response(self, result: dict, source: str, original_goal: str) -> dict:
        """格式化响应"""
        response = {
            "success": result.get("success", True),
            "source": source,
            "original_goal": original_goal,
            "timestamp": datetime.now().isoformat(),
        }

        # 优先使用 response，否则用 result
        if "response" in result:
            response["response"] = result["response"]
            response["result"] = result["response"]
        elif "result" in result:
            response["response"] = str(result["result"])
            response["result"] = result["result"]
        elif "error" in result:
            response["response"] = f"❌ {result['error']}"
            response["error"] = result["error"]

        return response


# ================================================================
#  全局单例
# ================================================================

skill = DoAnythingSkill()


def execute(params):
    """兼容 skill 调用接口"""
    return skill.execute(params)


if __name__ == "__main__":
    # 测试
    result = skill.execute({"goal": "你好"})
    print(result)
