"""Hermes 风格 Agent 执行器 - 增强版任务分解"""

import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.lib.agent_bus import get_bus
from core.lib.agent_registry import agent_registry
from core.lib.skill_loader_v3 import skill_loader
from core.lib.smart_adapter import smart_adapter


class HermesExecutor:
    """
    Hermes 风格 Agent 执行器 - 增强版

    核心能力:
    1. 深度任务分解 (Deep Decomposition)
    2. 工具调用 (Tool Use)
    3. 自我反思 (Self-Reflection)
    4. 迭代改进 (Iterative Improvement)
    """

    name = "hermes_executor"
    version = "2.0.0"

    def __init__(self):
        self.bus = get_bus()
        self.max_iterations = 3
        self.reflection_file = Path("data/hermes_reflections.json")
        self._load_reflections()

    def _load_reflections(self):
        import json

        if self.reflection_file.exists():
            with open(self.reflection_file, "r") as f:
                self.reflections = json.load(f)
        else:
            self.reflections = {
                "learnings": [],
                "patterns": [],
                "successful_strategies": [],
            }

    def _save_reflections(self):
        import json

        with open(self.reflection_file, "w") as f:
            json.dump(self.reflections, f, indent=2)

    def execute(self, goal: str, context: Dict = None) -> Dict:
        """执行任务 - 完整 Hermes 循环"""
        print(f"\n🧠 [Hermes v{self.version}] 开始处理: {goal[:80]}")

        # 阶段1: 深度任务分解
        subtasks = self._deep_decompose(goal)
        print(f"   📋 分解为 {len(subtasks)} 个子任务")

        if not subtasks:
            return {
                "success": False,
                "error": "无法分解任务",
                "source": "hermes_executor",
            }

        # 阶段2: 执行子任务
        results = []
        for i, subtask in enumerate(subtasks):
            desc = subtask.get("description", str(subtask))
            print(
                f"   🔧 执行子任务 {i+1}: {desc[:50] if isinstance(desc, str) else str(desc)[:50]}"
            )

            result = self._execute_subtask(subtask, context, i)
            results.append(result)

            if not result.get("success"):
                print(f"   ⚠️ 子任务 {i+1} 失败: {result.get('error')}")

                # 阶段3: 自我反思
                reflection = self._reflect(goal, subtasks, results, i)
                print(f"   💭 反思: {reflection.get('root_cause', '分析中')[:50]}")

                if reflection.get("should_retry") and i < self.max_iterations:
                    print(f"   🔄 重试子任务 {i+1}...")
                    retry_result = self._retry_subtask(subtask, reflection)
                    results[-1] = retry_result

        # 阶段4: 综合结果
        final_result = self._synthesize(goal, results)

        # 阶段5: 学习
        self._learn(goal, subtasks, results, final_result)

        return {
            "success": final_result.get("success", True),
            "result": final_result.get("output"),
            "subtasks": len(subtasks),
            "source": "hermes_executor",
        }

    def _deep_decompose(self, goal: str) -> List[Dict]:
        """深度任务分解 - 使用 LLM 智能拆解"""

        prompt = f"""将以下复杂任务分解为多个简单的子任务。

用户目标: {goal}

可用原子技能:
- search: 搜索信息
- summarize: 总结文本
- translate: 翻译文本
- vision: 图片识别
- write: 写作生成
- calculate: 数学计算

输出JSON格式，每个子任务包含:
{{
  "subtasks": [
    {{"step": 1, "action": "动作描述", "skill": "推荐技能", "input": "输入", "output": "输出变量名"}},
    {{"step": 2, "action": "动作描述", "skill": "推荐技能", "input": "{{step1.output}}", "output": "输出变量名"}}
  ],
  "reasoning": "分解理由"
}}

示例:
目标: "搜索AI信息，总结要点，写介绍"
输出:
{{
  "subtasks": [
    {{"step": 1, "action": "搜索人工智能相关信息", "skill": "search", "input": "人工智能", "output": "search_result"}},
    {{"step": 2, "action": "总结搜索结果为要点", "skill": "summarize", "input": "{{search_result}}", "output": "summary"}},
    {{"step": 3, "action": "根据要点写介绍", "skill": "write", "input": "{{summary}}", "output": "introduction"}}
  ]
}}"""

        response = smart_adapter.generate(prompt, auto_select=True)
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                subtasks = data.get("subtasks", [])
                if len(subtasks) >= 2:
                    print(f"   📝 分解为 {len(subtasks)} 个步骤")
                    for s in subtasks:
                        print(f"      步骤 {s.get('step')}: {s.get('action', '')[:40]}")
                    return subtasks
            except Exception as e:
                pass

        # 降级：返回单个任务
        return [
            {
                "step": 1,
                "action": goal,
                "skill": "llm",
                "input": goal,
                "output": "result",
            }
        ]

    def _execute_subtask(self, subtask: Dict, context: Dict, step: int) -> Dict:
        """执行单个子任务"""
        action = subtask.get("action", "")
        skill_name = subtask.get("skill", "llm")
        input_data = subtask.get("input", action)

        # 尝试使用技能
        if skill_name in skill_loader.list_skills():
            result = skill_loader.execute(
                skill_name, {"text": input_data, "goal": action}
            )
            if result.get("success"):
                return {
                    "success": True,
                    "output": result.get(
                        "result", result.get("translated", str(result))
                    ),
                    "skill": skill_name,
                    "step": step,
                }

        # 降级：使用 LLM
        prompt = f"执行: {action}\n输入: {input_data}"
        response = smart_adapter.generate(prompt, auto_select=True)

        return {
            "success": True,
            "output": response,
            "skill": "llm",
            "step": step,
            "fallback": True,
        }

    def _retry_subtask(self, subtask: Dict, reflection: Dict) -> Dict:
        """重试子任务"""
        alternative = reflection.get("alternative_skill", "llm")
        action = subtask.get("action", "")

        if alternative in skill_loader.list_skills():
            result = skill_loader.execute(alternative, {"text": action})
            if result.get("success"):
                return {
                    "success": True,
                    "output": result.get("result"),
                    "skill": alternative,
                    "retry": True,
                }

        response = smart_adapter.generate(action, auto_select=True)
        return {"success": True, "output": response, "skill": "llm", "retry": True}

    def _reflect(
        self, goal: str, subtasks: List, results: List, failed_idx: int
    ) -> Dict:
        """自我反思"""
        prompt = f"""分析失败原因。

目标: {goal}
失败步骤: {failed_idx + 1}
失败信息: {results[-1] if results else '未知'}

输出: {{"root_cause": "原因", "should_retry": true, "alternative_skill": "备选技能"}}"""

        response = smart_adapter.generate(prompt, auto_select=True)
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            return json.loads(match.group())

        return {"root_cause": "未知", "should_retry": True, "alternative_skill": "llm"}

    def _synthesize(self, goal: str, results: List) -> Dict:
        """综合结果"""
        outputs = [r.get("output", "") for r in results if r.get("success")]

        if not outputs:
            return {"success": False, "output": "无法完成任务"}

        if len(outputs) == 1:
            return {"success": True, "output": outputs[0]}

        prompt = f"""综合以下结果回答用户目标。

目标: {goal}
结果:
{chr(10).join([f'- {str(o)[:200] if isinstance(o, str) else str(o)[:200]}' for o in outputs])}

输出简洁答案。"""

        response = smart_adapter.generate(prompt, auto_select=True)
        return {"success": True, "output": response}

    def _learn(self, goal: str, subtasks: List, results: List, final: Dict):
        """学习经验"""
        success_count = sum(1 for r in results if r.get("success"))

        learning = {
            "goal": goal[:100],
            "subtask_count": len(subtasks),
            "success_rate": success_count / len(subtasks) if subtasks else 0,
            "skills_used": [r.get("skill") for r in results if r.get("skill")],
            "timestamp": datetime.now().isoformat(),
        }

        self.reflections["learnings"].append(learning)
        self.reflections["learnings"] = self.reflections["learnings"][-100:]

        if learning["success_rate"] >= 0.7:
            self.reflections["successful_strategies"].append(learning)
            self.reflections["successful_strategies"] = self.reflections[
                "successful_strategies"
            ][-50:]

        self._save_reflections()
        print(
            f"📚 Hermes 学习: {learning['goal'][:40]}... (成功率 {learning['success_rate']:.0%})"
        )


hermes_executor = HermesExecutor()
