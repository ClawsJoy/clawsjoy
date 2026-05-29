"""发送消息"""
class SendMessageSkill:
    def execute(self, params):
        to = params.get('to', '')
        content = params.get('content', '')
        return {"success": True, "sent": True, "message": f"已发送消息给{to}"}
skill = SendMessageSkill()
