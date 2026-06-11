import re

file_path = "agent_gateway_enhanced.py"

with open(file_path, 'r') as f:
    content = f.read()

# 在 enhanced_chat 函数中添加调试输出
old_func = '''def enhanced_chat():
    data = request.json or {}
    message = data.get("message", "")
    user_id = data.get("user_id", "guest")
    if not chat_engine.enabled:'''

new_func = '''def enhanced_chat():
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("=== enhanced_chat 被调用 ===")
    data = request.json or {}
    message = data.get("message", "")
    user_id = data.get("user_id", "guest")
    logger.info(f"message: {message}, user_id: {user_id}")
    
    if not chat_engine.enabled:
        logger.warning("chat_engine 未启用")
        return jsonify(
            {
                "success": False,
                "error": "服务暂时不可用",
                "response": "对话服务正在维护中，请稍后再试",
            }
        )
    logger.info("chat_engine 已启用")'''

content = content.replace(old_func, new_func)

with open(file_path, 'w') as f:
    f.write(content)

print("✅ 已添加调试日志")
