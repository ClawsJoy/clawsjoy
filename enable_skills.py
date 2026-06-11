import re

file_path = "core/lib/chat_engine.py"

with open(file_path, 'r') as f:
    content = f.read()

# 在 execute 方法中添加技能调用
old_llm = '''        try:
            resp = requests.post(
                self.llm_url,
                json={"message": message},
                timeout=60,
                headers={"Content-Type": "application/json"}
            )'''

new_llm = '''        # 先尝试匹配技能
        try:
            from core.lib.skill_loader_v3 import skill_loader
            skill_result = skill_loader.execute(message)
            if skill_result and skill_result.get("success"):
                return {
                    "success": True,
                    "response": skill_result.get("result", ""),
                    "agent": "skill",
                    "user_id": user_id
                }
        except Exception as e:
            print(f"[技能] 加载失败: {e}")
        
        try:
            resp = requests.post(
                self.llm_url,
                json={"message": message},
                timeout=60,
                headers={"Content-Type": "application/json"}
            )'''

content = content.replace(old_llm, new_llm)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ 技能调用已启用")
