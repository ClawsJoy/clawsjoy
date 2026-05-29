"""比价"""
class PriceCompareSkill:
    def execute(self, params):
        product = params.get('product', '')
        return {"success": True, "prices": {"京东": 99, "淘宝": 95, "拼多多": 89}, "best": "拼多多"}
skill = PriceCompareSkill()
