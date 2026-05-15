#!/usr/bin/env python3
"""
意图识别服务 - 专门做关键词匹配和任务路由
不处理聊天，只返回动作指令
"""

import json
import re
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

TASK_API = "http://redis:8084"


class IntentHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        if self.path == "/api/intent":
            self._handle_intent()
        else:
            self.send_error(404)

    def _detect_promo(self, msg):
        """宣传片意图"""
        # 动作词 + 目标词
        actions = ["制作", "生成", "做", "create", "make", "產生"]
        targets = ["宣传片", "宣傳片", "promo", "宣传视频", "宣傳視頻"]

        has_action = any(a in msg for a in actions)
        has_target = any(t in msg for t in targets)

        if has_action and has_target:
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
                "西安",
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

            return {"type": "promo", "city": city, "style": style}
        return None

    def _detect_library(self, msg):
        """资料库意图"""
        # 查询照片
        if any(k in msg for k in ["照片", "图片", "相册", "photo", "image"]):
            return {"type": "library", "action": "list"}
        return None

    def _detect_coffee(self, msg):
        """咖啡意图"""
        if "咖啡" in msg or "coffee" in msg:
            if "喝" in msg or "想" in msg or "order" in msg:
                return {"type": "coffee", "action": "shops"}
        return None

    def _handle_intent(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            message = data.get("message", "")

            print(f"意图分析: {message}", flush=True)

            # 按优先级检测
            result = self._detect_promo(message)
            if result:
                # 直接调用宣传片 API
                resp = requests.post(
                    f"{TASK_API}/api/task/promo",
                    json={
                        "city": result["city"],
                        "style": result["style"],
                        "tenant_id": "1",
                    },
                    timeout=60,
                )
                if resp.status_code == 200:
                    video_data = resp.json()
                    if video_data.get("success"):
                        self.send_json(
                            {"type": "promo", "video_url": video_data.get("video_url")}
                        )
                        return
                self.send_json({"type": "error", "message": "生成失败"})
                return

            result = self._detect_library(message)
            if result:
                resp = requests.get(
                    f"{TASK_API}/api/library/list",
                    params={"tenant_id": "1", "limit": 5},
                )
                if resp.status_code == 200:
                    files = resp.json().get("files", [])
                    if files:
                        names = [f["name"] for f in files[:5]]
                        self.send_json({"type": "library", "files": names})
                        return
                self.send_json({"type": "error", "message": "暂无照片"})
                return

            result = self._detect_coffee(message)
            if result:
                resp = requests.get("http://redis:8085/api/coffee/shops")
                if resp.status_code == 200:
                    shops = resp.json().get("shops", [])
                    if shops:
                        names = [s["name"] for s in shops[:3]]
                        self.send_json({"type": "coffee", "shops": names})
                        return
                self.send_json({"type": "error", "message": "咖啡店查询失败"})
                return

            # 未识别
            self.send_json({"type": "unknown", "message": message})

        except Exception as e:
            self.send_json({"type": "error", "message": str(e)})

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())


if __name__ == "__main__":
    port = 8088
    print(f"🎯 意图识别服务 on http://redis:{port}")
    HTTPServer(("0.0.0.0", port), IntentHandler).serve_forever()
