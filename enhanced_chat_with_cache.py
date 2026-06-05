"""增强聊天端点示例 - 带缓存"""

# 将此代码添加到 agent_gateway_enhanced.py 的 enhanced_chat 函数中


@app.route("/api/v5/enhanced/chat", methods=["POST"])
@monitor_performance
@rate_limit(limit=30, window=60)  # 每分钟30次
def enhanced_chat_with_cache():
    data = request.get_json() or {}
    user_id = data.get("user_id", "anonymous")
    message = data.get("message", "")

    if not message:
        return jsonify({"error": "message required"}), 400

    # 尝试从缓存获取
    cached = response_cache.get(user_id, message)
    if cached:
        return jsonify(
            {"success": True, "response": cached, "cached": True, "user_id": user_id}
        )

    # 调用 LLM 或其他处理
    try:
        # 这里调用实际的处理逻辑
        result = process_chat(user_id, message)

        # 缓存结果
        response_cache.set(user_id, message, result)

        return jsonify(
            {"success": True, "response": result, "cached": False, "user_id": user_id}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
