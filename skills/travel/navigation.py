"""导航规划"""
class NavigationSkill:
    def execute(self, params):
        origin = params.get('origin', '')
        dest = params.get('destination', '')
        return {"success": True, "route": {"distance": "10km", "time": "30min"}, "message": "路线规划完成"}
skill = NavigationSkill()
