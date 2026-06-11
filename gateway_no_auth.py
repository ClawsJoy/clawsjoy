#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

LLM_URL = "http://localhost:5012/chat"

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"})

@app.route("/api/v5/enhanced/chat", methods=["POST"])
def chat():
    data = request.json or {}
    message = data.get("message", "")
    user_id = data.get("user_id", "guest")
    
    if not message:
        return jsonify({"success": False, "response": "请输入消息"})
    
    try:
        resp = requests.post(LLM_URL, json={"message": message}, timeout=30)
        if resp.status_code == 200:
            return jsonify(resp.json())
        return jsonify({"success": False, "response": "服务错误"})
    except Exception as e:
        return jsonify({"success": False, "response": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
