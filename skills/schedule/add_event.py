"""添加日程事件"""
from datetime import datetime

class AddEventSkill:
    def execute(self, params):
        title = params.get('title', '')
        time_str = params.get('time', '')
        reminder = params.get('reminder', 15)  # 提前15分钟提醒
        
        # TODO: 存储到用户日历
        return {
            "success": True,
            "message": f"已添加日程: {title} at {time_str}",
            "event": {"title": title, "time": time_str, "reminder": reminder}
        }
skill = AddEventSkill()
