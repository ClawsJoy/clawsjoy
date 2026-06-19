import re

file_path = "engine/atomic/atomic_engine_v25.py"

with open(file_path, 'r') as f:
    content = f.read()

# 替换 _handle_skill 方法
old_skill = '''    def _handle_skill(self, json_data: Dict) -> Dict:
        return {"response": "技能系统处理中", "success": True}'''

new_skill = '''    def _handle_skill(self, json_data: Dict) -> Dict:
        """处理技能请求"""
        params = json_data.get("params", {})
        skill_action = params.get("skill", "list")
        user_id = json_data.get("user_id", "default")
        raw_input = json_data.get("raw_input", "")
        
        try:
            from core.lib.skill_recommender import skill_recommender
            
            if skill_action == "list":
                # 列出所有可用技能
                return skill_recommender.get_available_skills()
            elif skill_action == "install":
                # 安装技能
                skill_name = params.get("skill_name", "")
                return skill_recommender.install(skill_name, user_id)
            elif skill_action == "uninstall":
                # 卸载技能
                skill_name = params.get("skill_name", "")
                return skill_recommender.uninstall(skill_name)
            else:
                # 推荐技能
                return skill_recommender.recommend(raw_input, user_id)
        except Exception as e:
            return {"error": str(e), "response": f"技能处理失败: {e}", "success": False}'''

content = content.replace(old_skill, new_skill)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ _handle_skill 已修复 - 支持 list/install/uninstall/recommend")
