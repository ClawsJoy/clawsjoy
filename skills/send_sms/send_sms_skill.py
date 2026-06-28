"""短信 Skill — 返回短信指令给前端"""
def execute(params=None):
    params = params or {}
    phone = params.get("phone", "")
    message = params.get("message", "")
    return {
        "success": True,
        "action": "sms",
        "phone": phone,
        "message": message,
        "response": f"正在发送短信到{phone}"
    }
