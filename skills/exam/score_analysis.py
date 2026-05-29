"""考试成绩分析"""
class ScoreAnalysisSkill:
    def execute(self, params):
        scores = params.get('scores', {})
        subjects = ["语文", "数学", "英语", "科学"]
        
        analysis = {
            "total": sum(scores.values()),
            "average": sum(scores.values()) / len(scores) if scores else 0,
            "strength": max(scores, key=scores.get) if scores else "无",
            "weakness": min(scores, key=scores.get) if scores else "无"
        }
        return {"success": True, "analysis": analysis, "message": "成绩分析完成"}
skill = ScoreAnalysisSkill()
