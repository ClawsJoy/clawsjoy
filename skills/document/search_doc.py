"""搜索文档"""
class SearchDocSkill:
    def execute(self, params):
        keyword = params.get('keyword', '')
        return {"success": True, "results": [], "message": f"搜索 '{keyword}' 完成"}
skill = SearchDocSkill()
