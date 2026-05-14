"""内部审核器 - 大脑自己评估修复质量"""
from lib.memory_simple import memory

class SelfReviewerSkill:
    name = "self_reviewer"
    description = "内部审核，评估修复质量"
    version = "1.0.0"
    category = "quality"

    def execute(self, params):
        error_msg = params.get("error", "")
        fix = params.get("fix", "")
        validation = params.get("validation", {})
        
        # 自评分标准
        score = 0
        reasons = []
        
        # 1. 是否有修复方案
        if fix:
            score += 30
            reasons.append("有修复方案")
        else:
            reasons.append("无修复方案")
        
        # 2. 验证是否通过
        if validation.get("valid"):
            score += 40
            reasons.append("验证通过")
        elif validation.get("valid") is False:
            reasons.append("验证失败")
        else:
            score += 20
            reasons.append("无法验证")
        
        # 3. 修复类型评分
        if "pip install" in str(fix):
            score += 10
            reasons.append("模块安装类")
        elif "mkdir" in str(fix):
            score += 10
            reasons.append("目录创建类")
        elif "fuser" in str(fix):
            score += 5
            reasons.append("端口清理类")
        
        # 4. 综合评分
        if score >= 70:
            grade = "优秀"
            decision = "可入库"
        elif score >= 50:
            grade = "合格"
            decision = "可入库"
        else:
            grade = "不合格"
            decision = "需人工审核"
        
        # 记录审核结果
        memory.remember(
            f"self_review|{error_msg[:50]}|评分:{score}|等级:{grade}|决策:{decision}|原因:{','.join(reasons)}",
            category="self_review_log"
        )
        
        return {
            "score": score,
            "grade": grade,
            "decision": decision,
            "reasons": reasons,
            "can_auto_add": decision == "可入库"
        }

skill = SelfReviewerSkill()
