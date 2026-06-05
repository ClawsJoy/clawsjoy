#!/usr/bin/env python3
"""Smart Agent V2 - Smart Agent V2 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from core.lib.unified_config import unified_config

#!/usr/bin/env python3
"""真正智能 Agent v2 - 上下文记忆 + 完整意图识别"""

import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from core.lib.config_manager import config_manager


class SmartAgentV2:
    def __init__(self):
        self.session_history = {}
        self.agent_details = {
            "决策Agent": "决策Agent：用户总管，负责任务调度、技能编排、决策拍板",
            "聊天Agent": "聊天Agent：负责话术生成、用户沟通、自然语言交互",
            "执行Agent": "执行Agent：负责技能执行、任务运行、结果处理",
            "采集Agent": "采集Agent：负责参数收集、信息采集、上下文管理",
            "安全Agent": "安全Agent：负责安全检查、权限验证、审计日志",
            "分析Agent": "分析Agent：负责数据分析、优化建议、系统监控",
            "私人管家": "私人管家：用户的数字分身，1对1专属服务",
            "记忆Agent": "记忆Agent：负责记忆存储、回忆、向量搜索",
            "编排Agent": "编排Agent：负责任务规划、工作流管理",
            "代码Agent": "代码Agent：负责代码生成、审查、调试",
        }
        self.capabilities = [
            "回答系统相关问题",
            "列出 Agent 列表",
            "查询具体 Agent 职责",
            "列出可用技能",
            "生成架构图/蓝图",
            "记住对话上下文",
        ]

    def _get_session(self, user_id: str = "default") -> Dict:
        if user_id not in self.session_history:
            self.session_history[user_id] = {
                "history": [],
                "last_topic": None,
                "last_agents": [],
            }
        return self.session_history[user_id]

    def _extract_agent_name(self, text: str) -> Optional[str]:
        """提取 Agent 名称"""
        for agent in self.agent_details.keys():
            if agent in text:
                return agent
            # 去掉"Agent"后缀匹配
            base = agent.replace("Agent", "")
            if base in text:
                return agent
        return None

    def understand(self, user_input: str, session: Dict) -> Dict:
        """理解用户意图（带上下文）"""
        lower = user_input.lower()

        # 1. 问候
        if any(
            g in lower
            for g in ["你好", "hi", "hello", "嗨", "你是谁", "你干啥", "你叫什么"]
        ):
            return {"task": "greeting", "params": {}}

        # 2. 系统介绍
        if any(
            k in lower
            for k in ["clawsjoy是什么", "系统是什么", "介绍系统", "clawsjoy", "claws"]
        ):
            return {"task": "system_intro", "params": {}}

        # 3. Agent 列表
        if any(
            k in lower
            for k in ["有哪些 agent", "列出 agent", "agent 列表", "什么 agent"]
        ):
            return {"task": "list_agents", "params": {}}

        # 4. 具体 Agent 职责
        agent_name = self._extract_agent_name(user_input)
        if agent_name:
            return {"task": "agent_detail", "params": {"agent_name": agent_name}}

        # 5. 指代（它、这个、那个）→ 引用上一话题
        if any(k in lower for k in ["它", "这个", "那个", "他"]) and session.get(
            "last_topic"
        ):
            last_topic = session["last_topic"]
            if last_topic.startswith("agent_"):
                agent = last_topic.replace("agent_", "")
                return {"task": "agent_detail", "params": {"agent_name": agent}}

        # 6. 能力询问
        if any(
            k in lower for k in ["你会什么", "能做什么", "有什么功能", "capability"]
        ):
            return {"task": "list_capabilities", "params": {}}

        # 7. 技能列表
        if any(k in lower for k in ["技能", "skill"]):
            return {"task": "list_skills", "params": {}}

        # 8. 生成图表
        if any(k in lower for k in ["图", "chart", "架构图", "蓝图"]):
            return {"task": "generate_chart", "params": {}}

        return {"task": "unknown", "params": {}}

    def execute(self, task: str, params: dict, session: Dict) -> dict:
        """执行任务"""

        if task == "greeting":
            return {
                "success": True,
                "data": "你好！我是 ClawsJoy 智能助手，有什么可以帮你的？",
                "type": "text",
            }

        if task == "system_intro":
            intro = """ClawsJoy 是一个智能体操作系统，核心功能：
• 10个专业Agent协同工作
• 20+原子技能可调用
• 四层记忆系统（L0-L4）
• HTTPS + JWT 安全通信
• 用户数字分身和隐私保护
• 配置驱动架构"""
            return {"success": True, "data": intro, "type": "text"}

        if task == "list_agents":
            agents = list(self.agent_details.keys())
            session["last_topic"] = "list_agents"
            return {
                "success": True,
                "data": agents,
                "type": "list",
                "count": len(agents),
            }

        if task == "agent_detail":
            agent_name = params.get("agent_name", "")
            detail = self.agent_details.get(agent_name)
            if detail:
                session["last_topic"] = f"agent_{agent_name}"
                return {"success": True, "data": detail, "type": "text"}
            return {"success": False, "error": f"未找到 {agent_name}"}

        if task == "list_capabilities":
            return {
                "success": True,
                "data": self.capabilities,
                "type": "list",
                "count": len(self.capabilities),
            }

        if task == "list_skills":
            skills_dir = Path("unified_config.ROOT/skills")
            skills = [
                d.name
                for d in skills_dir.iterdir()
                if d.is_dir() and not d.name.startswith("_")
            ]
            session["last_topic"] = "list_skills"
            return {
                "success": True,
                "data": skills[:15],
                "count": len(skills),
                "type": "list",
            }

        if task == "generate_chart":
            from core.lib.education.retrieval_generator import RetrievalGenerator

            gen = RetrievalGenerator()
            svg = gen.generate_svg_content()
            filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.svg"
            file_path = Path("unified_config.ROOT/output") / filename
            file_path.write_text(svg, encoding="utf-8")
            session["last_topic"] = "generate_chart"
            return {"success": True, "data": str(file_path), "type": "file"}

        return {"success": False, "error": f"未知任务: {task}"}

    def process(self, user_input: str, user_id: str = "default") -> dict:
        start = time.time()
        session = self._get_session(user_id)

        # 理解意图（带上下文）
        intent = self.understand(user_input, session)
        task = intent["task"]

        # 执行
        result = self.execute(task, intent["params"], session)

        # 记录历史
        session["history"].append(
            {
                "input": user_input,
                "task": task,
                "success": result.get("success", False),
                "timestamp": datetime.now().isoformat(),
            }
        )
        # 只保留最近20条
        if len(session["history"]) > 20:
            session["history"] = session["history"][-20:]

        elapsed = (time.time() - start) * 1000

        return {
            "success": result.get("success", False),
            "data": result.get("data"),
            "type": result.get("type"),
            "task": task,
            "response_time_ms": round(elapsed, 2),
        }


agent = SmartAgentV2()


def format_output(result: dict) -> str:
    if not result.get("success"):
        return "抱歉，我没理解您的意思"

    data = result.get("data")
    output_type = result.get("type")

    if output_type == "list":
        if isinstance(data, list):
            if len(data) > 8:
                return f"共 {len(data)} 项：{', '.join(data[:8])} 等"
            return ", ".join(data)
    elif output_type == "text":
        return str(data)
    elif output_type == "file":
        return f"已生成: {data}"

    return str(data) if data else "处理完成"


if __name__ == "__main__":
    print("=" * 60)
    print("ClawsJoy 智能助手 v2 (真正智能)")
    print("=" * 60)
    print("输入 'exit' 退出\n")

    while True:
        try:
            user_input = input("👤 你: ")
            if user_input.lower() == "exit":
                break

            result = agent.process(user_input)
            output = format_output(result)
            print(f"🤖 助手: {output}")
            print(
                f"   [任务: {result.get('task')}, 耗时: {result.get('response_time_ms')}ms]\n"
            )

        except KeyboardInterrupt:
            print("\n再见！")
            break
