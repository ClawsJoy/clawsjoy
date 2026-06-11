import re

file_path = "agents/decision_agent/agent.py"

with open(file_path, 'r') as f:
    content = f.read()

# 修复 _save_memory 方法
old_save_memory = '''    def _save_memory(self):
        """保存决策记忆"""
        try:
            import json
            from pathlib import Path

            memory_file = Path(f"data/users/{self.user_id}/decision_memory.json")
            memory_file.parent.mkdir(parents=True, exist_ok=True)
            with open(memory_file, "w") as f:
            print(f"错误: {e}")
                json.dump([vars(r) for r in self._decision_memory[-200:]], f, indent=2)
        except Exception as e:
            pass'''

new_save_memory = '''    def _save_memory(self):
        """保存决策记忆"""
        try:
            import json
            from pathlib import Path

            memory_file = Path(f"data/users/{self.user_id}/decision_memory.json")
            memory_file.parent.mkdir(parents=True, exist_ok=True)
            with open(memory_file, "w") as f:
                json.dump([vars(r) for r in self._decision_memory[-200:]], f, indent=2)
        except Exception as e:
            print(f"保存记忆失败: {e}")'''

content = content.replace(old_save_memory, new_save_memory)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ 已修复 _save_memory 方法")
