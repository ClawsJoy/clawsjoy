"""日期差计算"""
from datetime import datetime
class DateDiffSkill:
    def execute(self, params):
        date1 = params.get('date1', '')
        date2 = params.get('date2', '')
        fmt = params.get('format', '%Y-%m-%d')
        d1 = datetime.strptime(date1, fmt)
        d2 = datetime.strptime(date2, fmt)
        days = (d2 - d1).days
        return {"success": True, "days": abs(days), "message": f"相差{abs(days)}天"}
skill = DateDiffSkill()
