"""发送会议邀请"""
class SendInviteSkill:
    def execute(self, params):
        title = params.get('title', '')
        time = params.get('time', '')
        emails = params.get('emails', [])
        return {"success": True, "invited": len(emails), "message": f"已邀请 {len(emails)} 人"}
skill = SendInviteSkill()
