"""添加跟进记录"""
class AddFollowupSkill:
    def execute(self, params):
        customer_id = params.get('customer_id', '')
        content = params.get('content', '')
        return {"success": True, "message": "已添加跟进记录"}
skill = AddFollowupSkill()
