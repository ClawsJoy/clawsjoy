import re

file_path = "agents/decision_agent/agent.py"

with open(file_path, 'r') as f:
    content = f.read()

# 增强决策者路由逻辑
new_routing = '''    def _decide_and_route(self, user_input: str, context: dict = None) -> dict:
        """决策路由 - 分发到对应 Agent"""
        
        # 1. 翻译 → translate_agent
        if "翻译" in user_input or "Translate" in user_input:
            from agents.translate_agent.agent import translate_agent
            return translate_agent.process(user_input, context)
        
        # 2. 代码 → code_agent
        if any(kw in user_input for kw in ["写代码", "代码", "编程", "函数", "Python"]):
            from agents.code_agent.agent import code_agent
            return code_agent.process(user_input, context)
        
        # 3. 数学 → calculator_agent
        import re
        if re.search(r'\\d+', user_input) and any(op in user_input for op in ['+', '-', '*', '/']):
            from agents.calculator_agent.agent import calculator_agent
            return calculator_agent.process(user_input, context)
        
        # 4. 记忆 → memory_agent
        if any(kw in user_input for kw in ["记住", "回忆", "忘记", "记忆"]):
            from agents.memory_agent.agent import memory_agent
            return memory_agent.process(user_input, context)
        
        # 5. 长任务 → orchestrator
        if len(user_input) > 30 and any(kw in user_input for kw in ["然后", "接着", "最后", "并且"]):
            from agents.orchestrator.agent import orchestrator
            return orchestrator.process(user_input, context)
        
        # 6. 默认 → chat_agent
        from agents.chat_agent.agent import chat_agent
        return chat_agent.process(user_input, context)'''

# 替换
start_marker = "    def _decide_and_route(self, user_input: str, context: dict = None) -> dict:"
start_idx = content.find(start_marker)
if start_idx != -1:
    end_marker = "\n    def "
    end_idx = content.find(end_marker, start_idx + len(start_marker))
    if end_idx == -1:
        end_idx = len(content)
    
    content = content[:start_idx] + new_routing + content[end_idx:]

with open(file_path, 'w') as f:
    f.write(content)

print("✅ 决策者路由已增强")
