#!/usr/bin/env python3
"""Play Quiz - Play Quiz 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

class QuizGameSkill:
    def execute(self, params):
        category = params.get('category', 'general')
        questions = {
            "general": {"question": "中国的首都是哪里？", "answer": "北京"},
            "history": {"question": "中华人民共和国成立于哪一年？", "answer": "1949"}
        }
        q = questions.get(category, questions["general"])
        user_answer = params.get('answer', None)
        if user_answer is None:
            return {"success": True, "question": q["question"]}
        else:
            correct = (user_answer == q["answer"])
            return {"success": True, "correct": correct, "message": "正确！" if correct else f"答案是{q['answer']}"}
skill = QuizGameSkill()
