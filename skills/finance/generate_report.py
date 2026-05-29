"""生成财务报告"""
class GenerateReportSkill:
    def execute(self, params):
        period = params.get('period', 'month')
        return {"success": True, "report": {"income": 50000, "expense": 30000, "profit": 20000}}
skill = GenerateReportSkill()
