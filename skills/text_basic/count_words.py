"""字数统计"""
class CountWordsSkill:
    def execute(self, params):
        text = params.get('text', '')
        words = text.split()
        chars = len(text)
        lines = text.count('\n') + 1
        return {"success": True, "words": len(words), "chars": chars, "lines": lines}
skill = CountWordsSkill()
