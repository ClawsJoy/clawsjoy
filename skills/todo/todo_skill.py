"""待办管理"""
import json, os

class todo_skill:
    name = "todo"
    description = "待办事项管理"
    version = "1.0.0"
    
    def __init__(self):
        self.file = "data/todos.json"
        os.makedirs(os.path.dirname(self.file), exist_ok=True)
    
    def execute(self, params):
        action = params.get("action", "list")
        todos = json.load(open(self.file)) if os.path.exists(self.file) else []
        if action == "add":
            todos.append({"task": params.get("task", ""), "done": False})
        elif action == "done":
            idx = params.get("index", 0)
            if idx < len(todos): todos[idx]["done"] = True
        json.dump(todos, open(self.file, 'w'))
        return {"success": True, "todos": todos}
