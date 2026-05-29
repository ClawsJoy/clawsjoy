"""点外卖"""
class OrderFoodSkill:
    def execute(self, params):
        items = params.get('items', [])
        address = params.get('address', '')
        return {"success": True, "order_id": f"ORD_{hash(str(items))}", "message": "订单已提交"}
skill = OrderFoodSkill()
