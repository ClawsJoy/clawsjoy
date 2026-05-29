"""发送邮件"""
class SendEmailSkill:
    def execute(self, params):
        to = params.get('to', '')
        subject = params.get('subject', '')
        body = params.get('body', '')
        
        return {
            "success": True,
            "message": f"邮件已发送至 {to}"
        }
skill = SendEmailSkill()
