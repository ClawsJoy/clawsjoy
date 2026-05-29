"""基金搜索"""
class FundSearchSkill:
    def execute(self, params):
        keyword = params.get('keyword', '')
        return {"success": True, "funds": [], "message": f"搜索{keyword}基金"}
skill = FundSearchSkill()
