"""时间查询"""
from datetime import datetime
class time_skill:
    name = "time"
    description = "时间查询"
    version = "1.0.0"
    def execute(self, params):
        now = datetime.now()
        return {"success": True, "now": now.isoformat(), "date": now.strftime("%Y-%m-%d"), "weekday": ["周一","周二","周三","周四","周五","周六","周日"][now.weekday()]}

# 标准入口：模块级 execute 函数
def execute(params=None):
    skill = time_skill()
    return skill.execute(params or {})
