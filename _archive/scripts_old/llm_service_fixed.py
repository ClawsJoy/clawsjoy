#!/usr/bin/env python3
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

MODEL = "phi3:mini"
OLLAMA_URL = "http://localhost:11434"

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model": MODEL})

@app.route("/chat", methods=["POST"])
def chat():
    # 确保请求有正确的 Content-Type
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json()
    message = data.get("message", "")

    if not message:
        return jsonify({"response": ""})

    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": MODEL, "prompt": message, "stream": False},
            timeout=60,
            headers={"Content-Type": "application/json"}
        )
        if resp.status_code == 200:
            result = resp.json()
            reply = result.get("response", "")
            return jsonify({"response": reply, "success": True})
        return jsonify({"response": "", "success": False})
    except Exception as e:
        return jsonify({"response": str(e), "success": False})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5012, debug=False)
