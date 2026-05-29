"""统计分析"""
class StatisticsSkill:
    def execute(self, params):
        numbers = params.get('numbers', [])
        if not numbers:
            return {"success": False, "error": "无数据"}
        total = sum(numbers)
        count = len(numbers)
        avg = total / count
        maximum = max(numbers)
        minimum = min(numbers)
        return {"success": True, "sum": total, "avg": avg, "max": maximum, "min": minimum, "count": count}
skill = StatisticsSkill()
