"""搜索客户"""
class SearchCustomerSkill:
    def execute(self, params):
        keyword = params.get('keyword', '')
        return {"success": True, "customers": [], "message": f"搜索客户 '{keyword}'"}
skill = SearchCustomerSkill()
