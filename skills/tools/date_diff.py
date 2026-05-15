"""
计算日期差
"""
class Date_diffSkill:
    name = "date_diff"
    description = "计算日期差"
    version = "1.0.0"
    category = "tools"
    
    def execute(self, params):
        from datetime import datetime; d1 = params.get('date1'); d2 = params.get('date2'); result = (datetime.strptime(d2, '%Y-%m-%d') - datetime.strptime(d1, '%Y-%m-%d')).days
        return {"success": True, "result": result}

skill = Date_diffSkill()
