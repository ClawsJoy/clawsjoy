file_path = "agent_gateway_enhanced.py"

with open(file_path, 'r') as f:
    content = f.read()

# 确保 enhanced_chat 使用 chat_engine 而不是 decision_agent
new_enhanced = '''@app.route("/api/v5/enhanced/chat", methods=["POST"])
@require_auth
def enhanced_chat():
    data = request.json or {}
    message = data.get("message", "")
    user_id = data.get("user_id", "guest")
    
    if not message:
        return jsonify({"success": False, "response": "请输入消息", "user_id": user_id})
    
    from core.lib.chat_engine import chat_engine
    result = chat_engine.execute(message, user_id)
    return jsonify(result)'''

import re
pattern = r'@app\.route\("/api/v5/enhanced/chat".*?def enhanced_chat\(\):.*?return jsonify\(result\)\n'
content = re.sub(pattern, new_enhanced, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ enhanced_chat 已修复")
