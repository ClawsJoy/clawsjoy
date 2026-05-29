"""完成待办事项"""
class CompleteTodoSkill:
    def execute(self, params):
        task_id = params.get('task_id', '')
        return {
            "success": True,
            "message": f"已完成待办 {task_id}"
        }
skill = CompleteTodoSkill()
