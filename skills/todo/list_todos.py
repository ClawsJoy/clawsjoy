"""列出待办事项"""
class ListTodosSkill:
    def execute(self, params):
        return {
            "success": True,
            "todos": [],
            "message": "暂无待办事项"
        }
skill = ListTodosSkill()
