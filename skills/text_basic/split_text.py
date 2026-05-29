"""文本分割"""
class SplitTextSkill:
    def execute(self, params):
        text = params.get('text', '')
        separator = params.get('separator', '\n')
        parts = text.split(separator)
        return {"success": True, "parts": parts, "count": len(parts)}
skill = SplitTextSkill()
