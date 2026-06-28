"""电话 Skill — 返回拨号指令给前端"""
def execute(params=None):
    params = params or {}
    phone = params.get("phone", "")
    name = params.get("name", "")
    return {
        "success": True,
        "action": "dial",
        "phone": phone,
        "name": name,
        "response": f"正在呼叫{name}({phone})..."
    }
