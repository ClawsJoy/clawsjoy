#!/usr/bin/env python3
"""Add Todo - Add Todo 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

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
