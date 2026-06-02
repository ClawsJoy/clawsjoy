#!/usr/bin/env python3
"""Math Quiz - Math Quiz 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

import random
class MathQuizSkill:
    def execute(self, params):
        level = params.get('level', 1)
        a = random.randint(1, 10 * level)
        b = random.randint(1, 10 * level)
        answer = params.get('answer', None)
        if answer is None:
            return {"success": True, "question": f"{a} + {b} = ?", "answer": a + b}
        else:
            correct = (answer == a + b)
            return {"success": True, "correct": correct, "message": "答对了！" if correct else f"不对哦，答案是{a+b}"}
skill = MathQuizSkill()
