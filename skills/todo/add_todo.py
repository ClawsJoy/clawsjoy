"""添加待办事项"""
class AddTodoSkill:
    def execute(self, params):
        task = params.get('task', '')
        priority = params.get('priority', 'medium')
        
        return {
            "success": True,
            "message": f"已添加待办: {task}",
            "todo": {"task": task, "priority": priority, "done": False}
        }
skill = AddTodoSkill()
