from lib.memory_simple import memory

class SatisfactionSkill:
    name = "satisfaction"
    description = "用户满意度回写，修正记忆权重"

    def execute(self, params):
        goal = params.get("goal")
        score = params.get("score", 0)  # 1-5 分
        comment = params.get("comment", "")

        # 查找最近一次该目标的执行记录
        history = memory.recall(goal, category="goal_execution_history")
        if not history:
            return {"success": False, "error": "未找到目标记录"}

        last = history[-1]

        # 写入满意度记录
        memory.remember(
            fact=f"用户反馈：{goal} -> 满意度={score}，评语={comment}，原计划={last}",
            category="user_satisfaction"
        )

        return {"success": True, "goal": goal, "score": score}

skill = SatisfactionSkill()
