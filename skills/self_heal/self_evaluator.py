"""自我评估 - 大脑自己评估任务质量"""
from lib.memory_simple import memory

class SelfEvaluatorSkill:
    name = "self_evaluator"
    description = "大脑自我评估"
    version = "1.0.0"
    category = "quality"

    def execute(self, params):
        task = params.get("task", "")
        result = params.get("result", {})
        
        # 计算自评分
        score = 0
        reasons = []
        
        if result.get("video") and result.get("duration", 0) > 30:
            score += 40
            reasons.append("视频生成成功")
        else:
            reasons.append("视频生成失败")
        
        if result.get("stages_passed", 0) >= 4:
            score += 30
            reasons.append("多环节通过")
        
        if score >= 70:
            grade = "优秀"
        elif score >= 50:
            grade = "合格"
        else:
            grade = "不合格"
        
        # 存入记忆
        memory.remember(
            f"自评|任务:{task[:50]}|得分:{score}|等级:{grade}|原因:{','.join(reasons)}",
            category="self_evaluation"
        )
        
        return {
            "score": score,
            "grade": grade,
            "reasons": reasons,
            "message": f"自我评估: {grade} ({score}分)"
        }

skill = SelfEvaluatorSkill()
