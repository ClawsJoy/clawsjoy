import re

file_path = "engine/atomic/atomic_engine_v25.py"

with open(file_path, 'r') as f:
    content = f.read()

# 修复 _handle_code：传递 context
old_handle_code = '''    def _handle_code(self, json_data: Dict) -> Dict:
        try:
            from agents.code_agent.agent_v4 import CodeAgentV4
            agent = CodeAgentV4(json_data.get("user_id", "default"))
            return agent.process(json_data.get("raw_input", ""))
        except Exception as e:
            return {"error": str(e)}'''

new_handle_code = '''    def _handle_code(self, json_data: Dict) -> Dict:
        try:
            from agents.code_agent.agent_v4 import CodeAgentV4
            agent = CodeAgentV4(json_data.get("user_id", "default"))
            # 构建 context，传递 session_id 用于记忆
            context = {
                "session_id": json_data.get("session_id"),
                "user_id": json_data.get("user_id", "default"),
                "raw_input": json_data.get("raw_input", "")
            }
            # 合并 params 中的 context
            if json_data.get("params") and json_data["params"].get("context"):
                context.update(json_data["params"]["context"])
            return agent.process(json_data.get("raw_input", ""), context)
        except Exception as e:
            return {"error": str(e)}'''

content = content.replace(old_handle_code, new_handle_code)

# 同样修复其他 handler
# _handle_write
old_handle_write = '''    def _handle_write(self, json_data: Dict) -> Dict:
        try:
            from agents.writer_agent.agent_v4 import WriterAgentV4
            agent = WriterAgentV4(json_data.get("user_id", "default"))
            return agent.process(json_data.get("raw_input", ""))
        except Exception as e:
            return {"error": str(e)}'''

new_handle_write = '''    def _handle_write(self, json_data: Dict) -> Dict:
        try:
            from agents.writer_agent.agent_v4 import WriterAgentV4
            agent = WriterAgentV4(json_data.get("user_id", "default"))
            context = {
                "session_id": json_data.get("session_id"),
                "user_id": json_data.get("user_id", "default"),
                "raw_input": json_data.get("raw_input", "")
            }
            if json_data.get("params") and json_data["params"].get("context"):
                context.update(json_data["params"]["context"])
            return agent.process(json_data.get("raw_input", ""), context)
        except Exception as e:
            return {"error": str(e)}'''

content = content.replace(old_handle_write, new_handle_write)

# 同样修复 translate
old_handle_translate = '''    def _handle_translate(self, json_data: Dict) -> Dict:
        try:
            from agents.translate_agent.agent_v4 import TranslateAgentV4
            agent = TranslateAgentV4(json_data.get("user_id", "default"))
            return agent.process(json_data.get("raw_input", ""))
        except Exception as e:
            return {"error": str(e)}'''

new_handle_translate = '''    def _handle_translate(self, json_data: Dict) -> Dict:
        try:
            from agents.translate_agent.agent_v4 import TranslateAgentV4
            agent = TranslateAgentV4(json_data.get("user_id", "default"))
            context = {
                "session_id": json_data.get("session_id"),
                "user_id": json_data.get("user_id", "default"),
                "raw_input": json_data.get("raw_input", "")
            }
            if json_data.get("params") and json_data["params"].get("context"):
                context.update(json_data["params"]["context"])
            return agent.process(json_data.get("raw_input", ""), context)
        except Exception as e:
            return {"error": str(e)}'''

content = content.replace(old_handle_translate, new_handle_translate)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ atomic_engine 已修复")
print("   - _handle_code: 传递 context")
print("   - _handle_write: 传递 context")
print("   - _handle_translate: 传递 context")
