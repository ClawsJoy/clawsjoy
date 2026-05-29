import logging

"""编排器 Agent - 真正任务分解和分发"""

import time
import requests
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
from core.agents.base.smart_agent import SmartAgent
from core.lib.workspace_manager import workspace_manager
from core.lib.smart_adapter import smart_adapter


class OrchestratorAgent(SmartAgent):
    """任务编排器 - 真正的任务分解"""

    name = "orchestrator"
    description = "任务编排与分发"
    type = "core"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self.behavior = workspace_manager.get_behavior_config("orchestrator")
        print(f"[Orchestrator] 初始化完成")

    def _save_record(self, to_agent: str, request: str, response: dict, duration_ms: float):
        """保存通信记录"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "from": self.name,
            "to": to_agent,
            "request": request,
            "response": response,
            "duration_ms": duration_ms,
            "user_id": self.user_id
        }
        log_dir = Path("data/exchange")
        log_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        with open(log_dir / filename, 'w') as f:
            json.dump(record, f, indent=2)

    def _llm_decompose(self, task: str) -> List[Dict]:
        """使用 LLM 分解任务"""
        prompt = f"""请将以下复杂任务分解为多个简单的子任务。

任务: {task}

可用 Agent:
- analysis_agent: 数据分析
- code_agent: 代码生成
- executor_agent: 计算执行
- chat_agent: 通用对话

输出 JSON 格式:
[
    {{"step": 1, "description": "子任务描述", "target": "目标Agent", "input": "输入参数"}},
    {{"step": 2, "description": "子任务描述", "target": "目标Agent", "input": "输入参数"}}
]

只输出 JSON 数组:"""

        try:
            response = smart_adapter.generate(prompt, auto_select=True)
            # 提取 JSON
            import re
            match = re.search(r'\[.*\]', response, re.DOTALL)
            if match:
                import json
                return json.loads(match.group())
        except Exception as e:
            print(f"LLM 分解失败: {e}")

        return [{"step": 1, "description": task, "target": "chat_agent", "input": task}]

    def _execute_subtask(self, subtask: Dict) -> Dict:
        """执行子任务"""
        target = subtask.get('target', 'chat_agent')
        description = subtask.get('description', '')
        input_data = subtask.get('input', description)

        start = time.time()
        resp = requests.post(
            f"http://localhost:5002/api/agent/{target}/message",
            json={"message": input_data, "user_id": self.user_id},
            timeout=30
        )
        duration_ms = (time.time() - start) * 1000
        result = resp.json() if resp.status_code == 200 else {"error": f"HTTP {resp.status_code}"}

        self._save_record(target, input_data, result, duration_ms)
        return result

    def _synthesize_results(self, subtasks: List, results: List) -> str:
        """综合结果"""
        if len(results) == 1:
            return results[0].get("response", "处理完成")

        # 多结果综合
        summary = f"已完成 {len(subtasks)} 个子任务:\n"
        for i, (subtask, result) in enumerate(zip(subtasks, results), 1):
            desc = subtask.get('description', '任务')[:50]
            resp = result.get('response', '完成')[:100]
            summary += f"{i}. {desc}: {resp}\n"

        return summary

    def process(self, user_input: str, context=None) -> Dict:
        """处理任务 - LLM 分解 + 执行"""
        print(f"[Orchestrator] 收到: {user_input}")

        decomposition = self.behavior.get('decomposition', {}) if self.behavior else {}

        if decomposition.get('enabled', True):
            # 使用 LLM 分解任务
            subtasks = self._llm_decompose(user_input)
            print(f"[Orchestrator] LLM 分解为 {len(subtasks)} 个子任务")

            if subtasks:
                # 执行子任务
                results = []
                for subtask in subtasks:
                    print(f"  执行: {subtask.get('description', '')[:50]} -> {subtask.get('target')}")
                    result = self._execute_subtask(subtask)
                    results.append(result)

                response = self._synthesize_results(subtasks, results)

                return {
                    "success": True,
                    "response": response,
                    "subtasks": subtasks,
                    "user_id": self.user_id,
                    "agent": self.name
                }

        return {"response": "无法处理该任务", "success": False, "user_id": self.user_id}


    def orchestrate(self, task: str, agents: list = None) -> dict:
        """编排任务"""
        agents = agents or (self.available_agents if hasattr(self, 'available_agents') else [])
        from datetime import datetime
        return {
            "task": task,
            "agents": agents,
            "status": "orchestrated",
            "timestamp": datetime.now().isoformat()
        }

    def schedule(self, task: str, schedule_time: str) -> dict:
        """调度任务"""
        return {
            "task": task,
            "scheduled_at": schedule_time,
            "status": "scheduled"
        }

    def dispatch(self, task: str, target_agent: str) -> dict:
        """分发任务到指定 Agent"""
        return {
            "task": task,
            "target": target_agent,
            "status": "dispatched"
        }

    def get_agents(self) -> list:
        """获取所有可用 Agent"""
        return self.available_agents if hasattr(self, 'available_agents') else []


# 全局实例
orchestrator_agent = OrchestratorAgent()
