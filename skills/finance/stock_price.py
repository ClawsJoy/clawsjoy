"""股票行情"""
class StockPriceSkill:
    def execute(self, params):
        code = params.get('code', '000001')
        return {"success": True, "stock": {"code": code, "price": 15.8, "change": 0.5, "percent": 3.2}}
skill = StockPriceSkill()
