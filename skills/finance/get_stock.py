"""查询股票信息"""
class GetStockSkill:
    def execute(self, params):
        code = params.get('code', '')
        return {
            "success": True,
            "stock": {"code": code, "price": 0, "change": 0},
            "message": f"股票 {code} 当前价格查询中"
        }
skill = GetStockSkill()
