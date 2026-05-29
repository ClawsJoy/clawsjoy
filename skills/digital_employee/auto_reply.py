"""自动回复"""
class AutoReplySkill:
    def execute(self, params):
        message = params.get('message', '')
        # 简单分类
        if "价格" in message:
            reply = "请查看我们的价目表"
        elif "售后" in message:
            reply = "售后问题请联系客服"
        else:
            reply = "已收到，我们会尽快处理"
        return {"success": True, "reply": reply}
skill = AutoReplySkill()
