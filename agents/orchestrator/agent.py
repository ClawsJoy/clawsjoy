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
        "video_indexer_agent",
        "memory_agent",
        "analysis_agent",
        "writer_agent",
        "code_agent",
        "vision_agent",
        "video_agent",
        "translate_agent",
        "collaboration_agent",
        "dialect_agent",
        "file_agent",
        "youtube_agent"
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
            if hasattr(agent, "handle"):
                sig = inspect.signature(agent.handle)
                if "context" in sig.parameters:
                    result = agent.handle(input_text, call_context)
                else:
                    result = agent.handle(input_text)
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



    def _load_decompose_rules(self):
        """从配置文件加载分解规则"""
        import yaml
        from pathlib import Path
        
        rules_path = Path("config/orchestrator_rules.yaml")
        if rules_path.exists():
            with open(rules_path) as f:
                config = yaml.safe_load(f)
                return config.get("rules", [])
        return []

    def _match_rule(self, task: str, rule: dict) -> bool:
        """检查规则是否匹配"""
        task_lower = task.lower()
        
        # 检查关键词
        patterns = rule.get("patterns", [])
        matched = any(pattern in task_lower for pattern in patterns)
        
        if not matched:
            return False
        
        # 检查条件
        condition = rule.get("condition")
        if condition:
            try:
                # 安全评估条件表达式
                if condition == "len(task) > 50":
                    return len(task) > 50
                elif condition == "len(task) <= 50":
                    return len(task) <= 50
                else:
                    return eval(condition)  # 需要更安全的方式
            except:
                return True
        
        return True

    def _decompose_task(self, task: str) -> List[Dict]:
        """配置驱动的任务分解"""
        rules = self._load_decompose_rules()
        
        for rule in rules:
            if self._match_rule(task, rule):
                steps = []
                for i, step in enumerate(rule.get("steps", []), 1):
                    steps.append({
                        "step": i,
                        "description": step.get("description", "任务处理"),
                        "agent": step.get("target"),
                        "input": step.get("input", task).replace("{task}", task)
                    })
                return steps
        
        # 默认
        return [{"step": 1, "description": "任务处理", "agent": "analysis_agent", "input": task}]


    def _get_agent(self, agent_name: str):
        """获取或创建 Agent 实例"""
        cache_key = f"{agent_name}:{self.user_id}"
        if not hasattr(self, '_agent_cache'):
            self._agent_cache = {}
        if cache_key not in self._agent_cache:
            try:
                module = __import__(f"agents.{agent_name}.agent", fromlist=[agent_name])
                for attr in dir(module):
                    if attr.endswith("Agent") and attr not in ["BusinessAgent", "BusinessAgentV2", "SmartAgent"]:
                        agent_class = getattr(module, attr)
                        self._agent_cache[cache_key] = agent_class(self.user_id)
                        print(f"[Orchestrator] 加载 Agent: {agent_name}")
                        break
            except Exception as e:
                print(f"[Orchestrator] 加载失败 {agent_name}: {e}")
                return None
        return self._agent_cache[cache_key]


    def process(self, user_input: str, context: dict = None) -> Dict:
        """编排主流程"""
        print(f"[Orchestrator] 📋 开始编排: {user_input[:50]}...")
        
        subtasks = self._decompose_task(user_input)
        print(f"[Orchestrator] 分解为 {len(subtasks)} 个子任务")
        
        results = []
        previous_result = None
        
        for i, subtask in enumerate(subtasks):
            if previous_result:
                subtask["previous_result"] = previous_result
            
            result = self._execute_subtask(subtask)
            results.append(result)
            
            if result.get("success"):
                previous_result = result.get("full_response") or result.get("response")
        
        final_response = self._aggregate_results(user_input, subtasks, results)
        
        return {
            "success": True,
            "response": final_response,
            "agent": self.name,
            "user_id": self.user_id
        }
