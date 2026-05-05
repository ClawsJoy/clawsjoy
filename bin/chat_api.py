#!/usr/bin/env python3
import json
import requests
import re
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

    # ========== 意图识别：多关键词组合 ==========
    def _detect_intent(self, msg):
        """
        返回: ('promo', {'city': '香港', 'style': '科技'})
              ('library', {'action': 'list'})
              ('chat', None)
        """
        msg_lower = msg.lower()

        # 1. 宣传片意图：必须同时包含“制作/生成/做” + “宣传片”
        promo_actions = ["制作", "生成", "做", "create", "make"]
        promo_keywords = ["宣传片", "宣傳片", "promo", "宣传视频"]

        has_action = any(a in msg for a in promo_actions)
        has_promo = any(k in msg for k in promo_keywords)

        if has_action and has_promo:
            # 提取城市
            city = "香港"
            cities = [
                "香港",
                "北京",
                "上海",
                "深圳",
                "广州",
                "杭州",
                "成都",
                "重庆",
                "武汉",
            ]
            for c in cities:
                if c in msg:
                    city = c
                    break
            # 提取风格
            style = "科技"
            if "复古" in msg:
                style = "复古"
            elif "温馨" in msg:
                style = "温馨"
            elif "大气" in msg:
                style = "大气"
            return ("promo", {"city": city, "style": style})

        # 2. 照片查询：包含“照片/图片/相册” + “找/查看/我的”
        photo_actions = ["找", "查看", "看", "我的", "show", "list"]
        photo_keywords = ["照片", "图片", "相册", "photo", "image"]

        has_photo_action = any(a in msg for a in photo_actions)
        has_photo_kw = any(k in msg for k in photo_keywords)

        if has_photo_action and has_photo_kw:
            return ("library", {"action": "list"})

        # 3. 简单照片查询（只说“照片”）
        if any(k in msg for k in photo_keywords):
            return ("library", {"action": "list"})

        # 4. 默认闲聊
        return ("chat", None)

    def _call_ollama(self, prompt):
        try:
            resp = requests.post(
                OLLAMA_API,
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"num_predict": 60, "temperature": 0.8},
                },
                timeout=25,
            )
            if resp.status_code == 200:
                return resp.json().get("response", "")
        except Exception as e:
            print(f"Ollama 错误: {e}")
        return None

    def _handle_chat(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            tenant_id = data.get("tenant_id", "1")
            message = data.get("message", "")

            print(f"收到: {message}", flush=True)

            # 意图识别
            intent, params = self._detect_intent(message)

            if intent == "promo":
                city = params.get("city", "香港")
                style = params.get("style", "科技")
                print(f"🎬 触发宣传片: {city}/{style}", flush=True)
                resp = requests.post(
                    f"{TASK_API}/api/task/promo",
                    json={"city": city, "style": style, "tenant_id": tenant_id},
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

            if intent == "library":
                print(f"📁 触发资料库查询", flush=True)
                resp = requests.get(
                    f"{TASK_API}/api/library/list",
                    params={"tenant_id": tenant_id, "limit": 5},
                )
                if resp.status_code == 200:
                    files = resp.json().get("files", [])
                    if files:
                        names = [f["name"] for f in files[:5]]
                        self.send_json(
                            {
                                "type": "text",
                                "message": f"📁 资料库: " + ", ".join(names),
                            }
                        )
                        return
                self.send_json({"type": "text", "message": "暂无照片"})
                return

            # 闲聊
            ai_reply = self._call_ollama(message)
            if ai_reply:
                self.send_json({"type": "text", "message": ai_reply[:150]})
            else:
                self.send_json(
                    {
                        "type": "text",
                        "message": "你可以说“制作北京宣传片”或“找我的照片”",
                    }
                )

        except Exception as e:
            print(f"错误: {e}", flush=True)
            self.send_json({"type": "text", "message": "服务异常，请稍后"})

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())


if __name__ == "__main__":
    port = 8087
    print(f"🎯 意图识别 Chat API on http://redis:{port}")
    HTTPServer(("0.0.0.0", port), ChatHandler).serve_forever()
