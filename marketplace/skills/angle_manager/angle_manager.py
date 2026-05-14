from skills.skill_interface import BaseSkill
import json
from pathlib import Path
from datetime import datetime

class AngleManagerSkill(BaseSkill):
    name = "angle_manager"
    description = "话题角度管理器（避免重复）"
    version = "1.0.0"
    category = "content"
    
    ANGLES_FILE = Path("/mnt/d/clawsjoy/output/history/angles_used.json")
    
    def _load_used(self):
        if self.ANGLES_FILE.exists():
            with open(self.ANGLES_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def _save_used(self, used):
        with open(self.ANGLES_FILE, 'w') as f:
            json.dump(used[-30:], f, ensure_ascii=False, indent=2)
    
    def execute(self, params):
        action = params.get("action", "get_available")
        topic = params.get("topic", "")
        
        if action == "get_available":
            used = self._load_used()
            used_angles = [a['angle'] for a in used]
            # 返回可用角度建议
            return {"success": True, "used_angles": used_angles, "available_count": 5}
        elif action == "mark_used":
            angle = params.get("angle", "")
            if angle:
                used = self._load_used()
                used.append({"angle": angle, "topic": topic, "date": datetime.now().isoformat()})
                self._save_used(used)
            return {"success": True}
        
        return {"success": False, "error": f"Unknown action: {action}"}

skill = AngleManagerSkill()
