"""联系老师"""
class ContactTeacherSkill:
    def execute(self, params):
        subject = params.get('subject', '')
        message = params.get('message', '')
        
        return {
            "success": True,
            "sent": True,
            "message": f"已向{subject}老师发送消息",
            "content": message[:50]
        }
skill = ContactTeacherSkill()
