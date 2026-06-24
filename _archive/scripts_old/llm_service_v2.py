#!/usr/bin/env python3
"""LLM 服务 V2 - 带数学预处理"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.lib.math_helper import math_helper

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL = "qwen2.5:3b"

# 优化的系统提示
SYSTEM_PROMPT = """你是 ClawsJoy 智能助手，具备以下能力：

1. **数学计算**：准确计算并给出步骤
2. **逻辑推理**：严格遵循逻辑规则
3. **代码生成**：提供可运行的代码
4. **多轮对话**：记住之前的对话内容

回答要求：
- 使用中文回答
- 给出清晰的步骤
- 直接回答问题，不要反问"""

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        message = data.get("message", "")

        # 预处理数学问题
        processed_message = message

        # 识别水池问题
        if math_helper.is_water_tank_problem(message):
            numbers = math_helper.extract_numbers_from_question(message)
            if len(numbers) >= 2:
                try:
                    inflow = float(numbers[0])
                    outflow = float(numbers[1])
                    result = math_helper.solve_water_tank(inflow, outflow)
                    if result:
                        logger.info(f"水池问题直接计算: {inflow}h/{outflow}h")
                        return jsonify({"response": result, "success": True})
                except:
                    pass

        # 通用处理
        full_prompt = f"""{SYSTEM_PROMPT}

用户问题: {processed_message}

请回答："""

        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": MODEL,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 1024,
                    "top_p": 0.9
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
    return jsonify({"model": MODEL, "status": "ok", "version": "2.0"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5012, debug=False)
