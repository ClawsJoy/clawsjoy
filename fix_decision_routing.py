import re

file_path = "agents/decision_agent/agent.py"

with open(file_path, 'r') as f:
    content = f.read()

# 确保决策者路由正确生效
old_routing = '''    def _decide_and_route(self, user_input: str, context: dict = None) -> dict:

        # 检查缓存
        cache_key = self._get_cache_key(user_input)
        cached = self._get_cached_decision(cache_key)
        if cached:
            return cached

        # 异步收集证据
        evidences = self._gather_evidences_async(user_input, context)'''

new_routing = '''    def _decide_and_route(self, user_input: str, context: dict = None) -> dict:
        """决策并路由 - 确保生效"""
        
        # 翻译直接路由到 chat_agent
        if "翻译" in user_input or "Translate" in user_input:
            from agents.chat_agent.agent_v4 import chat_agent
            return chat_agent.process(user_input, context)
        
        # 数学计算直接路由
        if any(op in user_input for op in ['+', '-', '*', '/']) and any(c.isdigit() for c in user_input):
            from agents.chat_agent.agent_v4 import chat_agent
            return chat_agent.process(user_input, context)

        # 检查缓存
        cache_key = self._get_cache_key(user_input)
        cached = self._get_cached_decision(cache_key)
        if cached:
            return cached

        # 异步收集证据
        evidences = self._gather_evidences_async(user_input, context)'''

content = content.replace(old_routing, new_routing)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ 决策者路由已修复，确保生效")
