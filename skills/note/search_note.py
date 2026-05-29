"""搜索笔记"""
class SearchNoteSkill:
    def execute(self, params):
        keyword = params.get('keyword', '')
        return {
            "success": True,
            "results": [],
            "message": f"搜索 '{keyword}' 找到 0 条笔记"
        }
skill = SearchNoteSkill()
