import re

file_path = "agents/decision_agent/agent.py"

with open(file_path, 'r') as f:
    content = f.read()

# 确保决策者正确调用其他 Agent
old_route = '''    def _route(self, decision: str, user_input: str, context: dict = None) -> dict:
        """执行路由"""
        if decision == "A":
            print(f"[决策者] 🚀 路由 → ChatAgent")
            agent = self._get_agent("chat")
            return (
                agent.handle(user_input)
                if agent
                else {"success": False, "error": "ChatAgent 不可用"}
            )
        elif decision == "B":
            print(f"[决策者] 🚀 路由 → ExecutorAgent")
            agent = self._get_agent("executor")
            return (
                agent.handle(user_input)
                if agent
                else {"success": False, "error": "ExecutorAgent 不可用"}
            )
        else:
            print(f"[决策者] 🚀 路由 → Orchestrator")
            agent = self._get_agent("orchestrator")
            return (
                agent.handle(user_input, {"caller": "decision_agent"})
                if agent
                else {"success": False, "error": "Orchestrator 不可用"}
            )'''

new_route = '''    def _route(self, decision: str, user_input: str, context: dict = None) -> dict:
        """执行路由 - 修复版"""
        print(f"[决策者] 🚀 路由决策: {decision}")
        
        # 翻译直接处理
        if "翻译" in user_input:
            from agents.chat_agent.agent import chat_agent
            return chat_agent.process(user_input, context)
        
        # 数学直接处理  
        import re
        if re.search(r'\\d+', user_input) and any(op in user_input for op in ['+', '-', '*', '/']):
            from agents.chat_agent.agent import chat_agent
            return chat_agent.process(user_input, context)
        
        if decision == "A":
            print(f"[决策者] 🚀 路由 → ChatAgent")
            agent = self._get_agent("chat")
            if agent:
                return agent.handle(user_input) if hasattr(agent, 'handle') else agent.process(user_input)
            return {"success": False, "error": "ChatAgent 不可用"}
        elif decision == "B":
            print(f"[决策者] 🚀 路由 → ExecutorAgent")
            agent = self._get_agent("executor")
            if agent:
                return agent.handle(user_input) if hasattr(agent, 'handle') else agent.process(user_input)
            return {"success": False, "error": "ExecutorAgent 不可用"}
        else:
            print(f"[决策者] 🚀 路由 → Orchestrator")
            agent = self._get_agent("orchestrator")
            if agent:
                return agent.handle(user_input, {"caller": "decision_agent"}) if hasattr(agent, 'handle') else agent.process(user_input)
            return {"success": False, "error": "Orchestrator 不可用"}'''

content = content.replace(old_route, new_route)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ 决策者路由已修复")
