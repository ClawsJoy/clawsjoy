"""酒店搜索"""
class HotelSearchSkill:
    def execute(self, params):
        city = params.get('city', '')
        checkin = params.get('checkin', '')
        checkout = params.get('checkout', '')
        return {"success": True, "hotels": [], "message": f"{city}酒店搜索结果"}
skill = HotelSearchSkill()
