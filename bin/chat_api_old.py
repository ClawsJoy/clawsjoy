#!/usr/bin/env python3
import json
import requests
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

TASK_API = "http://redis:8084"
OLLAMA_API = "http://redis:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"


class ChatHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/chat":
            self._handle_chat()
        else:
            self.send_error(404)

    def _call_ollama(self, prompt):
        """调用 Ollama，带重试"""
        for attempt in range(2):
            try:
                resp = requests.post(
                    OLLAMA_API,
                    json={
                        "model": OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"num_predict": 30, "temperature": 0.7},
                    },
                    timeout=30,
                )
                if resp.status_code == 200:
                    reply = resp.json().get("response", "")
                    if len(reply) > 80:
                        reply = reply[:80] + "..."
                    return reply
            except Exception as e:
                print(f"Ollama 尝试 {attempt+1} 失败: {e}")
                if attempt == 0:
                    time.sleep(2)
        return None

    def _handle_chat(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            tenant_id = data.get("tenant_id", "1")
            message = data.get("message", "")

            print(f"收到: {message}", flush=True)

            # 宣传片
            if "宣传片" in message:
                city = "香港"
                if "北京" in message:
                    city = "北京"
                elif "上海" in message:
                    city = "上海"
                resp = requests.post(
                    f"{TASK_API}/api/task/promo",
                    json={"city": city, "style": "科技", "tenant_id": tenant_id},
                    timeout=60,
                )
                if resp.status_code == 200:
                    result = resp.json()
                    if result.get("success"):
                        self.send_json(
                            {"type": "promo", "video_url": result.get("video_url")}
                        )
                        return
                self.send_json({"type": "text", "message": f"生成{city}宣传片失败"})
                return

            # 照片查询
            if any(k in message for k in ["照片", "图片", "相册"]):
                resp = requests.get(
                    f"{TASK_API}/api/library/list",
                    params={"tenant_id": tenant_id, "limit": 5},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    files = data.get("files", [])
                    if files:
                        names = [f["name"] for f in files[:3]]
                        self.send_json(
                            {
                                "type": "text",
                                "message": f"📁 你有 {len(files)} 个文件: "
                                + ", ".join(names),
                            }
                        )
                        return
                self.send_json({"type": "text", "message": "暂无照片"})
                return

            # AI 聊天
            ai_reply = self._call_ollama(message)
            if ai_reply:
                self.send_json({"type": "text", "message": ai_reply})
            else:
                self.send_json(
                    {
                        "type": "text",
                        "message": '你可以说"制作北京宣传片"或"找我的照片"',
                    }
                )

        except Exception as e:
            print(f"错误: {e}", flush=True)
            self.send_json({"type": "text", "message": "服务异常，请稍后重试"})

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())


if __name__ == "__main__":
    # 预热 Ollama
    try:
        requests.post(
            OLLAMA_API,
            json={"model": OLLAMA_MODEL, "prompt": "预热", "stream": False},
            timeout=5,
        )
        print("✅ Ollama 预热完成")
    except:
        print("⚠️ Ollama 预热失败")

    port = 8087
    print(f"🤖 Chat API on http://redis:{port}")
    HTTPServer(("0.0.0.0", port), ChatHandler).serve_forever()
