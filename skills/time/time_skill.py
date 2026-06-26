"""时间查询"""
from datetime import datetime

class time_skill:
    name = "time"
    description = "时间查询"
    version = "1.0.0"
    
    def execute(self, params):
        return {
            "success": True,
            "now": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "weekday": ["周一","周二","周三","周四","周五","周六","周日"][datetime.now().weekday()]
        }
