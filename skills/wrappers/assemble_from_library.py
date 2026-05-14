from skills.skill_interface import BaseSkill
import json
import random
from pathlib import Path

class AssembleFromLibrarySkill(BaseSkill):
    name = "assemble_from_library"
    description = "从内容库组装脚本"
    version = "1.0.0"
    category = "content"
    
    LIBRARY_FILE = Path("/mnt/d/clawsjoy/topics_library.json")
    
    def _load_library(self):
        if self.LIBRARY_FILE.exists():
            with open(self.LIBRARY_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def execute(self, params):
        action = params.get("action", "assemble")
        topic = params.get("topic", "")
        
        library = self._load_library()
        
        if action == "assemble":
            if not topic:
                # 随机选一个话题
                topics = list(library.keys())
                topic = random.choice(topics) if topics else "默认话题"
            
            data = library.get(topic, {})
            script = f"""🎬 开场（0:00-0:25）
{data.get("开场", f"今天聊聊{topic}")}

📌 第一个要点（0:25-1:00）
{data.get("要点1", "政策内容")}

📌 第二个要点（1:00-1:35）
{data.get("要点2", "申请条件")}

📌 第三个要点（1:35-2:10）
{data.get("要点3", "注意事项")}
"""
            return {"success": True, "script": script, "topic": topic}
        elif action == "list_topics":
            return {"success": True, "topics": list(library.keys())}
        
        return {"success": False, "error": f"Unknown action: {action}"}

skill = AssembleFromLibrarySkill()
