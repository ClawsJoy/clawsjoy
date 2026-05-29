"""监控品牌提及"""
class MonitorMentionSkill:
    def execute(self, params):
        brand = params.get('brand', '')
        return {"success": True, "mentions": 0, "message": f"{brand} 今日提及 0 次"}
skill = MonitorMentionSkill()
