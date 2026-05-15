#!/usr/bin/env python3
import json
import requests
import re
from http.server import HTTPServer, BaseHTTPRequestHandler

OLLAMA_API = "http://redis:11434/api/generate"
MODEL_EN = "phi:2.7b"  # 英文模型（快）
MODEL_ZH = "qwen2.5:3b"  # 中文模型


class AgentHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/agent":
            self._handle_agent()
        else:
            self.send_error(404)

    def _detect_language(self, text):
        """检测输入语言，返回 'zh' 或 'en'"""
        # 如果包含中文字符
        if re.search(r"[\u4e00-\u9fff]", text):
            return "zh"
        return "en"

    def _is_promo(self, text):
        patterns = [
            r"(制作|生成|做).{0,3}(宣传片|宣傳片)",
            r"生产片",
            r"產片",
            r"宣傳",
            r"promo",
        ]
        for p in patterns:
            if re.search(p, text, re.IGNORECASE):
                return True
        # 英文宣传片检测
        if "promo" in text.lower() or "video" in text.lower():
            return True
        return False

    def _extract_city(self, text):
        cities = [
            "香港",
            "北京",
            "上海",
            "深圳",
            "广州",
            "杭州",
            "成都",
            "Hong Kong",
            "Beijing",
            "Shanghai",
            "Shenzhen",
        ]
        for city in cities:
            if city in text:
                if city in ["Hong Kong", "Beijing", "Shanghai", "Shenzhen"]:
                    return {
                        "Hong Kong": "香港",
                        "Beijing": "北京",
                        "Shanghai": "上海",
                        "Shenzhen": "深圳",
                    }.get(city, "香港")
                return city
        return "香港"

    def _call_ollama(self, prompt, lang):
        model = MODEL_ZH if lang == "zh" else MODEL_EN
        # 根据语言设置不同的 prompt
        if lang == "zh":
            full_prompt = f"请用中文简短回复（30字以内）：{prompt}"
            max_tokens = 50
        else:
            full_prompt = f"Reply briefly in English (within 20 words): {prompt}"
            max_tokens = 60

        try:
            resp = requests.post(
                OLLAMA_API,
                json={
                    "model": model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {"num_predict": max_tokens, "temperature": 0.7},
                },
                timeout=30,
            )
            if resp.status_code == 200:
                reply = resp.json().get("response", "")
                # 限制长度
                if len(reply) > 150:
                    reply = reply[:150] + "..."
                return reply
        except Exception as e:
            print(f"Ollama 错误: {e}")
        return None

    def _handle_agent(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            user_input = data.get("message", "")

            print(f"📝 用户: {user_input}", flush=True)

            # 检测语言
            lang = self._detect_language(user_input)
            print(f"🌐 检测到语言: {lang}", flush=True)

            # 宣传片
            if self._is_promo(user_input):
                city = self._extract_city(user_input)
                resp = requests.post(
                    "http://redis:8084/api/task/promo",
                    json={"city": city, "style": "科技", "tenant_id": "1"},
                    timeout=60,
                )
                if resp.status_code == 200:
                    result = resp.json()
                    if result.get("success"):
                        self.send_json(
                            {"type": "promo", "video_url": result.get("video_url")}
                        )
                        return
                msg = (
                    f"生成{city}宣传片失败"
                    if lang == "zh"
                    else f"Failed to generate promo for {city}"
                )
                self.send_json({"type": "text", "message": msg})
                return

            # 照片查询
            if any(
                k in user_input
                for k in ["照片", "图片", "相册", "我的照片", "photo", "picture"]
            ):
                resp = requests.get(
                    "http://redis:8084/api/library/list",
                    params={"tenant_id": "1", "limit": 5},
                )
                if resp.status_code == 200:
                    files = resp.json().get("files", [])
                    if files:
                        names = [f["name"] for f in files[:5]]
                        if lang == "zh":
                            msg = f"📁 你有 {len(files)} 个文件: " + ", ".join(names)
                        else:
                            msg = f"📁 You have {len(files)} files: " + ", ".join(names)
                        self.send_json({"type": "text", "message": msg})
                        return
                msg = "暂无照片" if lang == "zh" else "No photos found"
                self.send_json({"type": "text", "message": msg})
                return

            # 普通聊天（自动语言）
            reply = self._call_ollama(user_input, lang)
            if reply:
                self.send_json({"type": "text", "message": reply})
            else:
                default_msg = (
                    "你好！有什么可以帮你的？"
                    if lang == "zh"
                    else "Hello! How can I help you?"
                )
                self.send_json({"type": "text", "message": default_msg})

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
    print(f"🤖 多语言 Agent: http://redis:{port}")
    print(f"   - 中文 → qwen2.5:3b")
    print(f"   - 英文 → phi:2.7b")
    HTTPServer(("0.0.0.0", port), AgentHandler).serve_forever()
