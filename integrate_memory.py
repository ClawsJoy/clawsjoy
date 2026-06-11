import re

file_path = "core/lib/chat_engine.py"

with open(file_path, 'r') as f:
    content = f.read()

# 在 execute 方法中添加记忆调用
old_execute = '''    def execute(self, message: str, user_id: str = "guest") -> Dict:
        """直接调用 LLM，不使用缓存"""
        import requests'''

new_execute = '''    def execute(self, message: str, user_id: str = "guest") -> Dict:
        """直接调用 LLM，集成记忆"""
        import requests
        
        # 1. 先回忆相关记忆
        try:
            from agents.memory_agent.agent import memory_agent
            memory_result = memory_agent.process(f"回忆 {message[:30]}", {"user_id": user_id})
            if memory_result.get("response"):
                print(f"[记忆] 相关记忆: {memory_result.get('response')}")
        except Exception as e:
            print(f"[记忆] 加载失败: {e}")'''

content = content.replace(old_execute, new_execute)

# 在返回前保存记忆
old_return = '''            return {
                    "success": True,
                    "response": result.get("response", ""),
                    "agent": "chat_engine",
                    "user_id": user_id
                }'''

new_return = '''            # 保存对话到记忆
            try:
                from agents.memory_agent.agent import memory_agent
                memory_agent.process(f"记住 {message[:50]}", {"user_id": user_id})
                memory_agent.process(f"记住 回复: {result.get('response', '')[:50]}", {"user_id": user_id})
            except Exception as e:
                pass
            
            return {
                    "success": True,
                    "response": result.get("response", ""),
                    "agent": "chat_engine",
                    "user_id": user_id
                }'''

content = content.replace(old_return, new_return)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ 记忆已集成到 chat_engine")
