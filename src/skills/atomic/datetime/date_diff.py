from lib.smart_config import smart_config
"""计算日期差"""
from datetime import datetime

class DateDiffSkill:
    name = "date_diff"
    description = "计算两个日期之间的天数差"
    version = "1.0.0"
    category = "datetime"
    
    def execute(self, params):
        date1 = params.get("date1", "")
        date2 = params.get("date2", "")
        
        if not date1 or not date2:
            return {"success": False, "error": "需要提供两个日期"}
        
        d1 = datetime.strptime(date1, "%Y-%m-%d")
        d2 = datetime.strptime(date2, "%Y-%m-%d")
        diff = (d2 - d1).days
        
        return {"success": True, "days": diff, "abs_days": abs(diff)}

skill = DateDiffSkill()
