"""关键词提取"""
class ExtractKeywordsSkill:
    def execute(self, params):
        text = params.get('text', '')
        import re
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z]+', text)
        from collections import Counter
        freq = Counter(words)
        keywords = [w for w, c in freq.most_common(5)]
        return {"success": True, "keywords": keywords}
skill = ExtractKeywordsSkill()
