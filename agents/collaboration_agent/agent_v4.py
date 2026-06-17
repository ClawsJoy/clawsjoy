#!/usr/bin/env python3
"""collaboration_agent v4.0 - 智慧化协作智能体"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import re
from typing import Dict, Optional, Tuple, List
from datetime import datetime

from core.agents.business.business_agent import BusinessAgent


class CollaborationAgentV4(BusinessAgent):
    """智慧化协作助手 - 多 Agent 协作"""

    name = "collaboration_agent_v4"
    description = "智慧化协作助手"
    version = "4.0.0"

    def __init__(self, user_id: str = "default"):
        super().__init__(user_id=user_id)
        self._tasks = []
        self._meetings = []
        print(f"🤝 {self.name} v{self.version} 智慧化启动")

    def can_handle_json(self, action: str, target: str) -> Tuple[bool, float]:
        capabilities = {
            ("delegate", "task"): (True, 0.90),
            ("schedule", "meeting"): (True, 0.85),
            ("assign", "task"): (True, 0.85),
            ("collaborate", "multi_agent"): (True, 0.90),
        }
        return capabilities.get((action, target), (False, 0.0))

    def _execute_business(self, user_input: str, context: Optional[Dict] = None) -> Dict:

        # 分配任务
        if any(kw in user_input for kw in ["分配任务", "指派", "交给"]):
            return self._assign_task(user_input)

        # 安排会议
        if any(kw in user_input for kw in ["安排会议", "预约会议", "开会"]):
            return self._schedule_meeting(user_input)

        # 委托给 Agent
        if any(kw in user_input for kw in ["委托", "调用", "使用"]):
            return self._delegate_to_agent(user_input)

        # 多 Agent 协作
        if any(kw in user_input for kw in ["协作", "先用", "再用", "并行", "同时"]):
            return self._collaborate(user_input)

        # 查看任务
        if "我的任务" in user_input or "任务列表" in user_input:
            return self._list_tasks()

        return self._response(self._get_help())

    def _assign_task(self, user_input: str) -> Dict:
        """分配任务"""
        match = re.search(r'(?:分配任务|指派|交给)[：:]\s*(.+?)(?:给|到)\s*(\w+)', user_input)
        if match:
            task, assignee = match.group(1), match.group(2)
        else:
            parts = user_input.replace("分配任务", "").strip().split()
            if len(parts) >= 2:
                task = " ".join(parts[:-1])
                assignee = parts[-1]
            else:
                return self._response("请指定任务和负责人。\n\n示例：分配任务 写报告 给 张三")

        task_item = {
            "id": len(self._tasks) + 1,
            "task": task,
            "assignee": assignee,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        self._tasks.append(task_item)

        return self._response(
            f"✅ 任务已分配\n\n📋 任务：{task}\n👤 负责人：{assignee}",
            metadata=task_item
        )

    def _schedule_meeting(self, user_input: str) -> Dict:
        """安排会议"""
        match = re.search(r'(?:安排会议|预约会议)[：:]\s*(.+?)(?:时间|在)\s*(.+)', user_input)
        if match:
            topic, time = match.group(1), match.group(2)
        else:
            time_match = re.search(r'(?:今天|明天|后天|\d+点|\d+:\d+)', user_input)
            time = time_match.group() if time_match else "待定"
            topic = re.sub(r'(?:安排会议|预约会议|时间|今天|明天|后天|\d+点|\d+:\d+)', '', user_input).strip()

        meeting = {
            "id": len(self._meetings) + 1,
            "topic": topic or "会议",
            "time": time,
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        }
        self._meetings.append(meeting)

        return self._response(
            f"📅 会议已安排\n\n📌 主题：{meeting['topic']}\n⏰ 时间：{meeting['time']}",
            metadata=meeting
        )

    def _delegate_to_agent(self, user_input: str) -> Dict:
        """委托给其他 Agent"""
        match = re.search(r'(?:委托|调用|使用)[：:]\s*(\w+)\s+(.+)', user_input)
        if not match:
            match = re.search(r'(\w+)_agent\s+(.+)', user_input)

        if match:
            agent_name = match.group(1)
            if not agent_name.endswith("_agent"):
                agent_name = f"{agent_name}_agent"
            task = match.group(2)
        else:
            return self._response("请指定 Agent 和任务。\n\n示例：委托 code_agent 写一个排序函数")

        from core.agents.wisdom.wisdom_factory import wisdom_factory
        target_agent = wisdom_factory.get_wisdom_agent(agent_name, self.user_id)

        if not target_agent:
            return self._response(f"❌ Agent {agent_name} 不可用")

        result = target_agent.process(task)

        return self._response(
            f"🤝 **委托执行**\n\n📌 Agent：{agent_name}\n📝 任务：{task}\n\n{result.get('response', '执行完成')}",
            metadata={"delegated_to": agent_name, "result": result}
        )

    def _collaborate(self, user_input: str) -> Dict:
        """多 Agent 协作"""
        print(f"[Collaboration] 收到输入: {user_input}")
        tasks = self._parse_collaboration_tasks(user_input)
        print(f"[Collaboration] 解析到任务: {tasks}")
        if not tasks:
            return self._response("请指定协作任务。\n\n示例：先用 analysis_agent 分析数据，再用 code_agent 生成报表")
        
        results = []
        for task in tasks:
            agent_name = task.get("agent")
            subtask = task.get("task")
            
            if not agent_name or not subtask:
                continue
            
            from core.agents.wisdom.wisdom_factory import wisdom_factory
            target_agent = wisdom_factory.get_wisdom_agent(agent_name, self.user_id)
            
            if target_agent:
                result = target_agent.process(subtask)
                results.append({
                    "agent": agent_name,
                    "task": subtask,
                    "result": result.get("response", "完成"),
                    "success": result.get("success", True)
                })
            else:
                results.append({
                    "agent": agent_name,
                    "task": subtask,
                    "result": f"Agent {agent_name} 不可用",
                    "success": False
                })
        
        output = "🤝 **多 Agent 协作结果**\n\n"
        for r in results:
            status = "✅" if r["success"] else "❌"
            output += f"{status} **{r['agent']}**: {r['task'][:50]}\n"
            output += f"   {r['result'][:150]}\n\n"
        
        return self._response(output, metadata={"collaboration_results": results})

    def _parse_collaboration_tasks(self, text: str) -> List[Dict]:
        """解析协作任务 - 增强版"""
        tasks = []

        # 更宽松的匹配模式
        # 模式1: 先用 X_agent 做 Y，再用 Z_agent 做 W
        pattern1 = r'先用\s*(\w+_agent)\s*(?:做|执行|处理|分析|生成|写)\s*([^，,。再用]+)'
        matches1 = re.findall(pattern1, text)
        for agent_name, task_content in matches1:
            tasks.append({"agent": agent_name, "task": task_content.strip()})

        # 模式2: 再用 X_agent 做 Y
        pattern2 = r'再用\s*(\w+_agent)\s*(?:做|执行|处理|分析|生成|写)\s*([^，,。]+)'
        matches2 = re.findall(pattern2, text)
        for agent_name, task_content in matches2:
            tasks.append({"agent": agent_name, "task": task_content.strip()})

        # 模式3: 用 X_agent 做 Y
        pattern3 = r'用\s*(\w+_agent)\s*(?:做|执行|处理|分析|生成|写)\s*([^，,。再用]+)'
        matches3 = re.findall(pattern3, text)
        for agent_name, task_content in matches3:
            tasks.append({"agent": agent_name, "task": task_content.strip()})

        # 模式4: X_agent 做 Y
        pattern4 = r'(\w+_agent)\s*(?:做|执行|处理|分析|生成|写)\s*([^，,。再用]+)'
        matches4 = re.findall(pattern4, text)
        for agent_name, task_content in matches4:
            tasks.append({"agent": agent_name, "task": task_content.strip()})

        # 去重
        seen = set()
        unique_tasks = []
        for t in tasks:
            key = f"{t['agent']}_{t['task']}"
            if key not in seen:
                seen.add(key)
                unique_tasks.append(t)

        return unique_tasks



    def _list_tasks(self) -> Dict:
        """列出任务"""
        if not self._tasks:
            return self._response("暂无任务")

        pending = [t for t in self._tasks if t.get("status") == "pending"]
        completed = [t for t in self._tasks if t.get("status") == "completed"]

        lines = ["📋 **任务列表**"]
        if pending:
            lines.append("\n⏳ 进行中：")
            for t in pending:
                lines.append(f"  {t['id']}. {t['task']} (负责人: {t['assignee']})")
        if completed:
            lines.append("\n✅ 已完成：")
            for t in completed:
                lines.append(f"  {t['id']}. {t['task']}")

        return self._response("\n".join(lines))

