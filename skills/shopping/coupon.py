"""优惠券查询"""
class CouponSkill:
    def execute(self, params):
        store = params.get('store', '')
        return {"success": True, "coupons": ["满100减10", "满200减30"], "message": "可用优惠券"}
skill = CouponSkill()
