"""列出日程事件"""
class ListEventsSkill:
    def execute(self, params):
        date = params.get('date', 'today')
        # TODO: 从用户日历读取
        return {
            "success": True,
            "events": [],
            "message": f"{date} 暂无日程"
        }
skill = ListEventsSkill()
