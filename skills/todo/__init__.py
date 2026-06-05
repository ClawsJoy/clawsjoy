"""
todo 技能模块
"""

from .todo_skill import ListTodosSkill


def execute(params=None):
    """统一执行入口"""
    skill = ListTodosSkill()
    return skill.execute(params)
