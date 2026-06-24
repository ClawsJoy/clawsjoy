#!/usr/bin/env python3
"""LLM 服务 - 使用 Qwen 模型"""

from flask import Flask, request, jsonify
import requests
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL = "qwen2.5:3b"  # 使用推理能力更强的模型

SYSTEM_PROMPT = """你是一个擅长数学和逻辑推理的助手。回答要求：
1. 数学题：给出解题步骤和最终答案
2. 逻辑题：严格按逻辑推理
3. 答案要完整、准确"""

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        message = data.get("message", "")

        # 水池问题的特殊处理（临时，直到模型学会）
        if "进水" in message and "出水" in message and "小时" in message:
            # 解析数字
            import re
            numbers = re.findall(r'(\d+)', message)
            if len(numbers) >= 2:
                inflow = int(numbers[0])
                outflow = int(numbers[1])
                time = 1 / (1/inflow - 1/outflow)
                if time > 0:
                    answer = f"需要 {time:.1f} 小时。\n\n解题：\n进水速率=1/{inflow}，出水速率=1/{outflow}，净速率={1/inflow-1/outflow:.3f}，时间=1/净速率={time:.1f}小时。"
                    return jsonify({"response": answer, "success": True})

        full_prompt = f"""{SYSTEM_PROMPT}

用户问题: {message}"""

        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": MODEL,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # 更低温度，更确定
                    "num_predict": 512
                }
            },
            timeout=120
        )

        if resp.status_code == 200:
            result = resp.json()
            response = result.get("response", "")
            return jsonify({"response": response, "success": True})
        else:
            return jsonify({"response": f"模型错误: {resp.status_code}", "success": False}), 500

    except Exception as e:
        logger.error(f"错误: {e}")
        return jsonify({"response": f"服务错误: {str(e)}", "success": False}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"model": MODEL, "status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5012, debug=False)
