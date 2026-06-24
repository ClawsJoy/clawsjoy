#!/usr/bin/env python3
"""增强版 LLM 服务 - 优化推理能力"""

from flask import Flask, request, jsonify
import requests
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 优化的系统提示词 - 增强推理能力
SYSTEM_PROMPT = """你是一个智能助手，具备强大的推理能力。请遵循以下规则：

1. **逻辑推理**：严格遵循逻辑规则，不要产生悖论。例如：如果所有A都是B，且C是A，则C一定是B。

2. **数学计算**：逐步计算并给出最终答案。对于常见题型使用标准公式。

3. **准确性优先**：不确定时不要编造，承认不确定。

4. **回答简洁**：直接给出答案，避免冗长解释。

5. **中文优先**：使用中文回答，除非用户要求其他语言。"""

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        message = data.get("message", "")

        # 构建带系统提示的完整消息
        full_prompt = f"""{SYSTEM_PROMPT}

用户问题: {message}

请仔细思考后回答："""

        # 调用 Ollama
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "phi3:mini",
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # 降低温度，提高准确性
                    "top_p": 0.9,
                    "num_predict": 512  # 限制输出长度
                }
            },
            timeout=60
        )

        if resp.status_code == 200:
            result = resp.json()
            response = result.get("response", "")
            return jsonify({"response": response, "success": True})
        else:
            return jsonify({"response": f"Ollama 错误: {resp.status_code}", "success": False}), 500

    except Exception as e:
        logger.error(f"错误: {e}")
        return jsonify({"response": f"服务错误: {str(e)}", "success": False}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": "phi3:mini"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5012, debug=False)
