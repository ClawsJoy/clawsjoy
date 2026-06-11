file_path = "agent_gateway_enhanced.py"

with open(file_path, 'r') as f:
    content = f.read()

# 添加调试日志
old_func = '''def enhanced_chat():
    data = request.json or {}
    message = data.get("message", "")
    user_id = data.get("user_id", "guest")'''

new_func = '''def enhanced_chat():
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("enhanced_chat 被调用")
    
    data = request.json or {}
    message = data.get("message", "")
    user_id = data.get("user_id", "guest")
    logger.info(f"message: {message}, user_id: {user_id}")'''

content = content.replace(old_func, new_func)

# 在返回前也添加日志
old_return = '''    return jsonify(result)'''
new_return = '''    logger.info(f"返回结果: {result.get('response', '')[:100]}")
    return jsonify(result)'''

content = content.replace(old_return, new_return)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ 已添加调试日志")
