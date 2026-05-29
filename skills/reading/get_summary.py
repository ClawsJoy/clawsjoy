"""获取书籍摘要"""
class GetSummarySkill:
    def execute(self, params):
        book = params.get('book', '')
        return {"success": True, "summary": f"《{book}》内容摘要...", "key_points": ["要点1", "要点2", "要点3"]}
skill = GetSummarySkill()
