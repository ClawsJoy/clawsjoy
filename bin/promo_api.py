#!/usr/bin/env python3
"""
宣传片制作 API - 自动采集图片 + 生成视频
"""

import subprocess
import json
import os
import time
import glob
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from settings import CLAWSJOY_ROOT, PORT_PROMO
from py_logging import get_logger

CLAWSJOY_BIN = str(CLAWSJOY_ROOT / "bin")
IMAGES_DIR = "/root/.openclaw/web/images"
OUTPUT_DIR = "/root/.openclaw/web/videos"
LOGGER = get_logger("promo_api")

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_latest_image_dir():
    """获取最新采集完成的图片目录。"""
    dirs = glob.glob(f"{IMAGES_DIR}/*/")
    if not dirs:
        return None
    return max(dirs, key=os.path.getctime)

def make_promo(city, style="科技"):
    """执行宣传片生产流程：采图 -> 生成视频 -> 返回结果。"""
    keyword = f"{city}{style}"
    
    # 1) 采集图片素材
    LOGGER.info("采集图片: %s", keyword)
    spider_cmd = f"{CLAWSJOY_BIN}/spider_unsplash '{keyword}' 5"
    subprocess.run(spider_cmd, shell=True, timeout=60)
    
    # 2) 短暂等待素材落盘
    time.sleep(3)
    
    # 3) 定位本次任务的图片目录
    img_dir = get_latest_image_dir()
    if not img_dir:
        return {"success": False, "message": "图片采集失败"}
    
    LOGGER.info("图片目录: %s", img_dir)
    
    # 4) 调用 make_video 生成视频
    output_file = f"{OUTPUT_DIR}/{city}_{style}_{int(time.time())}.mp4"
    script = f"{keyword}宣传片\n探索{city}的{style}魅力"
    
    video_cmd = f"{CLAWSJOY_BIN}/make_video '{script}' '{img_dir}' '{output_file}' '{keyword}'"
    LOGGER.info("执行视频命令: %s", video_cmd)
    
    result = subprocess.run(video_cmd, shell=True, timeout=120, capture_output=True, text=True)
    
    # 5) 校验输出文件是否有效
    if os.path.exists(output_file) and os.path.getsize(output_file) > 10000:
        return {
            "success": True,
            "message": f"✅ {city}{style}宣传片已生成",
            "video_url": f"/videos/{os.path.basename(output_file)}",
            "size": os.path.getsize(output_file)
        }
    else:
        return {"success": False, "message": f"视频生成失败: {result.stderr[:200]}"}

class PromoHandler(BaseHTTPRequestHandler):
    """宣传片制作 API 处理器。"""

    def do_GET(self):
        """支持 GET 方式触发宣传片制作。"""
        parsed = urlparse(self.path)
        if parsed.path == '/api/promo/make':
            params = parse_qs(parsed.query)
            city = params.get('city', ['香港'])[0]
            style = params.get('style', ['科技'])[0]
            
            result = make_promo(city, style)
            self.send_json(result)
        else:
            self.send_error(404)
    
    def do_POST(self):
        """支持 POST 方式触发宣传片制作。"""
        if self.path == '/api/promo/make':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            city = body.get('city', '香港')
            style = body.get('style', '科技')
            
            result = make_promo(city, style)
            self.send_json(result)
        else:
            self.send_error(404)
    
    def send_json(self, data):
        """统一 JSON 响应并附带基础 CORS 头。"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def log_message(self, format, *args):
        LOGGER.info(format % args)

if __name__ == "__main__":
    port = PORT_PROMO
    LOGGER.info("Promo API started: http://localhost:%s", port)
    HTTPServer(("0.0.0.0", port), PromoHandler).serve_forever()
