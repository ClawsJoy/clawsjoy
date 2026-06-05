"""Orchestrator - 任务编排器 v5.1"""

import sys

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

import inspect
from typing import Dict, List, Optional

from core.agents.business.business_agent_v2 import BusinessAgentV2


class OrchestratorAgent(BusinessAgentV2):
    """任务编排器 - 分解子任务，调度其他 Agent"""

    name = "orchestrator"
    description = "任务编排与分发"
    version = "5.1.0"

    AVAILABLE_AGENTS = [
        "analysis_agent",
        "calculator_agent",
        "translate_agent",
        "code_agent",
        "writer_agent",
        "vision_agent",
        "video_agent",
    ]

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._agent_cache = {}
        self.subtask_results = []
        # 确保 engines 存在（BusinessAgentV2 应该已初始化）
        if not hasattr(self, "engines"):
            self.engines = {}
        print(f"[Orchestrator] v{self.version} 初始化完成")

    def _execute_business(self, user_input: str, context: Dict = None) -> Dict:
        return self.process(user_input, context)

    def process(self, user_input: str, context: dict = None) -> Dict:
        print(f"[Orchestrator] 📋 开始编排: {user_input[:50]}...")

        subtasks = self._decompose_task(user_input)
        print(f"[Orchestrator] 分解为 {len(subtasks)} 个子任务")

        results = []
        previous_result = None

        for i, subtask in enumerate(subtasks):
            print(
                f"[Orchestrator] 执行子任务 {i+1}/{len(subtasks)}: {subtask.get('agent')}"
            )

            if previous_result:
                subtask["previous_result"] = previous_result
                print(f"[Orchestrator] 传递前置结果给子任务 {i+1}")

            result = self._execute_subtask(subtask)
            results.append(result)

            if result.get("success"):
                previous_result = result.get("full_response") or result.get("response")

        final_response = self._aggregate_results(user_input, subtasks, results)

        return {
            "success": True,
            "response": final_response,
            "subtasks_count": len(subtasks),
            "subtask_results": results,
            "agent": self.name,
            "user_id": self.user_id,
        }

    def _decompose_task(self, task: str) -> List[Dict]:
        task_lower = task.lower()

        # 分析 + 写作
        if "分析" in task_lower and ("写" in task_lower or "总结" in task_lower):
            return [
                {"step": 1, "description": "数据分析", "agent": "analysis_agent", "input": task},
                {"step": 2, "description": "撰写报告", "agent": "writer_agent", "input": "根据分析结果写总结报告"},
            ]
        # 纯分析
        if "分析" in task_lower:
            return [{"step": 1, "description": "数据分析", "agent": "analysis_agent", "input": task}]
        
        # 代码生成
        if any(kw in task_lower for kw in ["代码", "函数", "写一个", "编程", "实现"]):
            return [{"step": 1, "description": "代码生成", "agent": "code_agent", "input": task}]
        
        # 图像识别
        if any(kw in task_lower for kw in ["识别", "描述图片", "看图", "图像识别", "vision"]):
            return [{"step": 1, "description": "图像识别", "agent": "vision_agent", "input": task}]
        
        # 视频处理
        if any(kw in task_lower for kw in ["裁剪", "转码", "截图", "合成", "视频", "video"]):
            return [{"step": 1, "description": "视频处理", "agent": "video_agent", "input": task}]
        
        # 复杂计算
        if any(kw in task_lower for kw in ["复杂计算", "科学计算", "矩阵", "微积分", "方程"]):
            return [{"step": 1, "description": "数学计算", "agent": "calculator_agent", "input": task}]
        
        # 长文本翻译
        if "翻译" in task_lower and len(task) > 50:
            return [{"step": 1, "description": "文本翻译", "agent": "translate_agent", "input": task}]
        
        # 默认交给分析
        return [{"step": 1, "description": "任务处理", "agent": "analysis_agent", "input": task}]

    def _get_agent(self, agent_name: str):
        cache_key = f"{agent_name}:{self.user_id}"
        if cache_key not in self._agent_cache:
            try:
                module = __import__(f"agents.{agent_name}.agent", fromlist=[agent_name])
                for attr in dir(module):
                    if attr.endswith("Agent") and attr not in [
                        "BusinessAgent",
                        "BusinessAgentV2",
                        "SmartAgent",
                    ]:
                        agent_class = getattr(module, attr)
                        self._agent_cache[cache_key] = agent_class(self.user_id)
                        print(f"[Orchestrator] 加载 Agent: {agent_name}")
                        break
            except Exception as e:
                print(f"[Orchestrator] 加载失败 {agent_name}: {e}")
                return None
        return self._agent_cache[cache_key]

    def _execute_subtask(self, subtask: Dict) -> Dict:
        agent_name = subtask.get("agent", "analysis_agent")
        input_text = subtask.get("input", subtask.get("description", ""))

        call_context = {}
        if "previous_result" in subtask:
            call_context["previous_result"] = subtask["previous_result"]
            prev = (
                subtask["previous_result"][:500]
                if len(subtask["previous_result"]) > 500
                else subtask["previous_result"]
            )
            input_text = f"{input_text}\n\n【上一任务结果】\n{prev}"

        agent = self._get_agent(agent_name)
        if not agent:
            return {
                "step": subtask.get("step"),
                "agent": agent_name,
                "success": False,
                "response": f"Agent {agent_name} 无法加载",
                "full_response": "",
            }

        try:
            if hasattr(agent, "process"):
                sig = inspect.signature(agent.process)
                if "context" in sig.parameters:
                    result = agent.process(input_text, call_context)
                else:
                    result = agent.process(input_text)
            else:
                result = agent.handle(input_text)

            return {
                "step": subtask.get("step"),
                "agent": agent_name,
                "success": result.get("success", True),
                "response": result.get("response", "")[:500],
                "full_response": result.get("response", ""),
            }
        except Exception as e:
            print(f"[Orchestrator] 子任务失败: {e}")
            import traceback

            traceback.print_exc()
            return {
                "step": subtask.get("step"),
                "agent": agent_name,
                "success": False,
                "response": f"执行失败: {str(e)[:100]}",
                "full_response": "",
            }

    def _aggregate_results(
        self, original_task: str, subtasks: List[Dict], results: List[Dict]
    ) -> str:
        if not results:
            return "任务执行失败"

        if len(results) == 1:
            return results[0].get("response", "任务完成")

        summary = f"✅ 已完成 {len(results)} 个子任务：\n\n"
        for i, (subtask, result) in enumerate(zip(subtasks, results), 1):
            status = "✅" if result.get("success") else "❌"
            summary += f"**步骤 {i}: {subtask.get('description', '任务')}** {status}\n"
            summary += f"   {result.get('response', '完成')[:300]}\n\n"

        return summary


orchestrator_agent = OrchestratorAgent()
