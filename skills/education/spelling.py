"""拼写练习"""
class SpellingSkill:
    def execute(self, params):
        word = params.get('word', 'apple')
        user_spelling = params.get('spelling', '')
        if not user_spelling:
            return {"success": True, "question": f"请拼写: {word}", "correct": word}
        else:
            correct = (user_spelling.lower() == word.lower())
            return {"success": True, "correct": correct, "message": "拼写正确！" if correct else f"正确拼写是 {word}"}
skill = SpellingSkill()
