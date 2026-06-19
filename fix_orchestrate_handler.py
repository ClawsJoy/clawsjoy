import re

file_path = "engine/atomic/atomic_engine_v25.py"

with open(file_path, 'r') as f:
    content = f.read()

# 替换 _handle_orchestrate 方法
old_handler = '''    def _handle_orchestrate(self, json_data: Dict) -> Dict:
        try:
            from agents.orchestrator.agent_v4 import OrchestratorV4
            agent = OrchestratorV4(json_data.get("user_id", "default"))
            return agent.process(json_data.get("raw_input", ""))
        except Exception as e:
            return {"error": str(e), "response": f"编排失败: {e}"}'''

new_handler = '''    def _handle_orchestrate(self, json_data: Dict) -> Dict:
        try:
            from agents.orchestrator.agent_v4 import OrchestratorV4
            agent = OrchestratorV4(json_data.get("user_id", "default"))
            result = agent.process(json_data.get("raw_input", ""))
            # 确保返回字典
            if not isinstance(result, dict):
                return {"response": str(result), "success": True}
            return result
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": str(e), "response": f"编排失败: {e}", "success": False}'''

content = content.replace(old_handler, new_handler)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ _handle_orchestrate 已修复")
