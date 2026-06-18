#!/usr/bin/env python3
"""CollaborationAgent v4.2 - 精简稳定版（多 Agent 协作）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from typing import Dict, Optional, Tuple, List
from datetime import datetime

from core.agents.business.business_agent import BusinessAgent


class CollaborationAgentV4(BusinessAgent):
    """协作 Agent - 精简稳定版"""

    name = "collaboration_agent_v4"
    description = "智慧协作助手"
    version = "4.2.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._tasks = []
        print(f"🤝 CollaborationAgent v{self.version} 启动")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        return (True, 0.85)

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        t = user_input.lower()
        
        if any(kw in t for kw in ["分配任务", "指派", "交给"]):
            return self._assign_task(user_input)
        
        if any(kw in t for kw in ["协作", "先用", "再用", "并行"]):
            return self._collaborate(user_input)
        
        if any(kw in t for kw in ["委托", "调用", "使用"]) and "_agent" in t:
            return self._delegate_to_agent(user_input)
        
        if any(kw in t for kw in ["查看任务", "任务列表"]):
            return self._list_tasks()
        
        return self._resp("🤝 输入「分配任务 写报告 给 code_agent」、「协作 先用 analysis_agent 分析数据 再用 code_agent 生成报表」或「委托 code_agent 写代码」")

    # ================================================================
    #  分配任务
    # ================================================================

    def _assign_task(self, user_input: str) -> Dict:
        match = re.search(r'(?:分配任务|指派|交给)[：:]\s*(.+?)(?:给|到)\s*(\w+)', user_input)
        if match:
            task, assignee = match.group(1).strip(), match.group(2).strip()
        else:
            parts = user_input.replace("分配任务", "").strip().split()
            if len(parts) >= 2:
                task = " ".join(parts[:-1])
                assignee = parts[-1]
            else:
                return self._resp("请指定任务和负责人。示例：分配任务 写报告 给 张三")
        
        self._tasks.append({
            "id": len(self._tasks) + 1,
            "task": task,
            "assignee": assignee,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        })
        return self._resp(f"✅ 任务已分配\n\n📋 {task}\n👤 {assignee}")

    # ================================================================
    #  委托
    # ================================================================

    def _delegate_to_agent(self, user_input: str) -> Dict:
        match = re.search(r'(?:委托|调用|使用)[：:]\s*(\w+_agent)\s*(.+)', user_input)
        if not match:
            match = re.search(r'(\w+_agent)\s+(.+)', user_input)
        if not match:
            return self._resp("请指定 Agent 和任务。示例：委托 code_agent 写排序函数")
        
        agent_name, task = match.group(1), match.group(2)
        
        try:
            from core.agents.wisdom.wisdom_factory import wisdom_factory
            agent = wisdom_factory.get_wisdom_agent(agent_name, self.user_id)
            if not agent:
                return self._resp(f"❌ Agent {agent_name} 不可用")
            
            result = agent.process(task)
            return self._resp(f"🤝 委托 {agent_name}\n\n{result.get('response', '执行完成')}")
        except Exception as e:
            return self._resp(f"❌ 委托失败: {e}")

    # ================================================================
    #  协作
    # ================================================================

    def _collaborate(self, user_input: str) -> Dict:
        tasks = self._parse_tasks(user_input)
        if not tasks:
            return self._resp("请指定协作任务。示例：先用 analysis_agent 分析数据，再用 code_agent 生成报表")
        
        results = []
        for task in tasks:
            agent_name = task.get("agent")
            subtask = task.get("task")
            if not agent_name or not subtask:
                continue
            
            try:
                from core.agents.wisdom.wisdom_factory import wisdom_factory
                agent = wisdom_factory.get_wisdom_agent(agent_name, self.user_id)
                if agent:
                    result = agent.process(subtask)
                    results.append({"agent": agent_name, "task": subtask, "result": result.get("response", "完成"), "success": True})
                else:
                    results.append({"agent": agent_name, "task": subtask, "result": f"Agent {agent_name} 不可用", "success": False})
            except Exception as e:
                results.append({"agent": agent_name, "task": subtask, "result": str(e), "success": False})
        
        output = "🤝 协作结果\n\n"
        for r in results:
            output += f"{'✅' if r['success'] else '❌'} {r['agent']}: {r['result'][:150]}\n\n"
        return self._resp(output)

    def _parse_tasks(self, text: str) -> List[Dict]:
        tasks = []
        # 先用 X_agent 做 Y
        pattern1 = r'先用\s*(\w+_agent)\s*(?:做|执行|处理|分析|生成|写)\s*([^，,。再用]+)'
        for agent, task in re.findall(pattern1, text):
            tasks.append({"agent": agent, "task": task.strip()})
        # 再用 X_agent 做 Y
        pattern2 = r'再用\s*(\w+_agent)\s*(?:做|执行|处理|分析|生成|写)\s*([^，,。]+)'
        for agent, task in re.findall(pattern2, text):
            tasks.append({"agent": agent, "task": task.strip()})
        # 去重
        seen = set()
        return [t for t in tasks if f"{t['agent']}_{t['task']}" not in seen and not seen.add(f"{t['agent']}_{t['task']}")]

    # ================================================================
    #  列出任务
    # ================================================================

    def _list_tasks(self) -> Dict:
        if not self._tasks:
            return self._resp("📭 暂无任务")
        
        pending = [t for t in self._tasks if t.get("status") == "pending"]
        if not pending:
            return self._resp("🎉 所有任务已完成！")
        
        lines = ["📋 待办任务："]
        for t in pending:
            lines.append(f"  {t['id']}. {t['task']} (负责人: {t['assignee']})")
        return self._resp("\n".join(lines))

    # ================================================================
    #  辅助
    # ================================================================

    def _resp(self, content: str, **kwargs) -> Dict:
        return {"success": True, "response": content, "output_content": content, **kwargs}


if __name__ == "__main__":
    agent = CollaborationAgentV4("test")
    print(agent.process("委托 code_agent 写排序函数")["response"])
