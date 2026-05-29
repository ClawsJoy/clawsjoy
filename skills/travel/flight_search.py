"""机票搜索"""
class FlightSearchSkill:
    def execute(self, params):
        from_city = params.get('from', '')
        to_city = params.get('to', '')
        date = params.get('date', '')
        return {"success": True, "flights": [], "message": f"搜索{from_city}到{to_city}机票"}
skill = FlightSearchSkill()
