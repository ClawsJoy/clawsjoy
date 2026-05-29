import logging

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config

from core.lib.unified_config import unified_config
#!/usr/bin/env python3
"""真正智能 Agent v3 - 完整意图"""

import sys
import time
from pathlib import Path
from datetime import datetime
from core.lib.config_manager import config_manager



class SmartAgentV3:
    def __init__(self):
        self.agent_details = {
            "决策Agent": "决策Agent：用户总管，负责任务调度、技能编排、决策拍板",
            "聊天Agent": "聊天Agent：负责话术生成、用户沟通、自然语言交互",
            "执行Agent": "执行Agent：负责技能执行、任务运行、结果处理",
            "采集Agent": "采集Agent：负责参数收集、信息采集、上下文管理",
            "安全Agent": "安全Agent：负责安全检查、权限验证、审计日志",
            "分析Agent": "分析Agent：负责数据分析、优化建议、系统监控",
            "私人管家": "私人管家：用户的数字分身，1对1专属服务",
        }
    
    def understand(self, user_input: str):
        lower = user_input.lower().strip()

        if any(k in lower for k in ['你好', 'hi', 'hello', '你是谁', '你叫什么', '你干啥', '你能干嘛']):
            return {"task": "greeting"}

        if any(k in lower for k in ['clawsjoy', '系统是什么', '介绍', 'claws']):
            return {"task": "intro"}

        if any(k in lower for k in ['有哪些 agent', '列出 agent', 'agent 列表', '什么 agent', 'agent有哪些']):
            return {"task": "list_agents"}

        for agent in self.agent_details.keys():
            if agent in user_input:
                return {"task": "agent_detail", "agent": agent}

        if any(k in lower for k in ['会什么', '能做什么', '有什么功能', '能力']):
            return {"task": "capabilities"}

        if any(k in lower for k in ['技能', 'skill']):
            return {"task": "list_skills"}

        if any(k in lower for k in ['图', 'chart', '架构图', '蓝图']):
            return {"task": "generate_chart"}

        return {"task": "unknown"}
    
    def execute(self, task: str, agent: str = None):
        if task == "greeting":
            return "你好！我是 ClawsJoy 智能助手。我可以帮你了解系统、查询 Agent、列出技能、生成图表等。"

        if task == "intro":
            return """ClawsJoy 是一个智能体操作系统，核心功能：
• 10个专业Agent协同工作
• 20+原子技能可调用
• 四层记忆系统（L0-L4）
• HTTPS + JWT 安全通信
• 用户数字分身和隐私保护"""

        if task == "list_agents":
            agents = list(self.agent_details.keys())
            return f"共有 {len(agents)} 个专业 Agent：{', '.join(agents)}"

        if task == "agent_detail" and agent:
            return self.agent_details.get(agent, f"未找到 {agent} 的详细信息")

        if task == "capabilities":
            return """我能帮你：
• 介绍 ClawsJoy 系统
• 列出所有 Agent 及其职责
• 查询具体 Agent 的详细信息
• 列出可用技能
• 生成系统架构图"""

        if task == "list_skills":
            skills_dir = Path("unified_config.ROOT/skills")
            skills = [d.name for d in skills_dir.iterdir() if d.is_dir() and not d.name.startswith('_')]
            return f"共有 {len(skills)} 个原子技能：{', '.join(skills[:10])}" + (" 等" if len(skills) > 10 else "")

        if task == "generate_chart":
            try:
                from core.lib.education.retrieval_generator import RetrievalGenerator
                gen = RetrievalGenerator()
                svg = gen.generate_svg_content()
                filename = f"chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.svg"
                file_path = Path("unified_config.ROOT/output") / filename
                file_path.write_text(svg, encoding='utf-8')
                return f"已生成架构图：{file_path}"
            except Exception as e:
                return f"生成图表失败：{e}"

        return "抱歉，我没理解您的意思。你可以试试问：有哪些 Agent？、ClawsJoy 是什么？、你会什么？"
    
    def process(self, user_input: str):
        start = time.time()
        intent = self.understand(user_input)
        response = self.execute(intent.get("task"), intent.get("agent"))
        elapsed = (time.time() - start) * 1000

        return {
            "response": response,
            "task": intent.get("task"),
            "time_ms": round(elapsed, 2)
        }


if __name__ == "__main__":
    agent = SmartAgentV3()
    
    print("=" * 60)
    print("ClawsJoy 智能助手 v3")
    print("=" * 60)
    
    tests = [
        "你是谁",
        "你干啥的",
        "clawsjoy是什么",
        "有哪些 Agent",
        "决策Agent是干什么的",
        "你会什么",
        "有哪些技能",
        "生成架构图"
    ]
    
    for test in tests:
        print(f"\n👤 {test}")
        result = agent.process(test)
        print(f"🤖 {result['response'][:300]}")
        print(f"   [任务: {result['task']}, 耗时: {result['time_ms']}ms]")
