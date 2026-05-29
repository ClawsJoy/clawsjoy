"""设置提醒"""
class SetReminderSkill:
    def execute(self, params):
        content = params.get('content', '')
        time_str = params.get('time', '')
        
        return {
            "success": True,
            "message": f"已设置提醒: {content} at {time_str}",
            "reminder": {"content": content, "time": time_str}
        }
skill = SetReminderSkill()
