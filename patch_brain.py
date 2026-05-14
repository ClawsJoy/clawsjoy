import re

file_path = "agent_gateway.py"

with open(file_path, 'r') as f:
    content = f.read()

# 为 security_chat 添加大脑记录
brain_code = '''
    # 记录到大脑
    try:
        from agent_core.brain_enhanced import brain
        brain.record_experience(
            agent="web_chat",
            action=message[:200],
            result={"success": True, "user": user_id},
            context="security_chat"
        )
    except:
        pass
'''

# 在 security_chat 函数中添加
if 'brain.record_experience' not in content:
    # 找到 security_chat 函数中的位置
    content = content.replace(
        'response, protected = gate.chat(message)',
        'response, protected = gate.chat(message)\n' + brain_code
    )
    
    with open(file_path, 'w') as f:
        f.write(content)
    print("✅ security_chat 已添加大脑记录")
else:
    print("✅ security_chat 已有大脑记录")

# 为 /api/chat 添加大脑记录
if '@app.route(\'/api/chat\'' in content:
    old_chat = '''def chat():
    try:
        msg = request.json.get('message', '')
        if not msg:
            return jsonify({'error': 'Empty message'}), 400
        resp = requests.post("http://localhost:11434/api/generate",
            json={"model": "llama3.2:3b", "prompt": msg, "stream": False}, timeout=60)
        return jsonify({'message': resp.json().get('response', ''), 'status': 'ok'})'''
    
    new_chat = '''def chat():
    try:
        msg = request.json.get('message', '')
        if not msg:
            return jsonify({'error': 'Empty message'}), 400
        resp = requests.post("http://localhost:11434/api/generate",
            json={"model": "llama3.2:3b", "prompt": msg, "stream": False}, timeout=60)
        response = resp.json().get('response', '')
        
        # 记录到大脑
        try:
            from agent_core.brain_enhanced import brain
            brain.record_experience(
                agent="chat_api",
                action=msg[:200],
                result={"success": True, "response": response[:100]},
                context="direct_chat"
            )
        except:
            pass
        
        return jsonify({'message': response, 'status': 'ok'})'''
    
    if 'brain.record_experience' not in content:
        content = content.replace(old_chat, new_chat)
        with open(file_path, 'w') as f:
            f.write(content)
        print("✅ /api/chat 已添加大脑记录")
    else:
        print("✅ /api/chat 已有大脑记录")
