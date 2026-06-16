import re

file_path = "agent_gateway_enhanced.py"

with open(file_path, 'r') as f:
    content = f.read()

# 新的 enhanced_chat - 使用决策者路由
new_enhanced = '''@app.route("/api/v5/enhanced/chat", methods=["POST"])
@require_auth
def enhanced_chat():
    data = request.json or {}
    message = data.get("message", "")
    user_id = data.get("user_id", "guest")
    
    if not message:
        return jsonify({"success": False, "response": "请输入消息", "user_id": user_id})
    
    # 使用决策者进行智能路由
    from agents.decision_agent.agent_v4 import decision_agent
    result = decision_agent.process(message, {"user_id": user_id})
    
    return jsonify(result)'''

# 找到并替换
pattern = r'@app\.route\("/api/v5/enhanced/chat".*?def enhanced_chat\(\):.*?return jsonify\(result\)\n'
content = re.sub(pattern, new_enhanced, content, flags=re.DOTALL)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ enhanced_chat 已修改为使用决策者路由")
