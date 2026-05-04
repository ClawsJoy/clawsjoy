import importlib, sys, os
from skill_loader import load_skill, list_skills
#!/usr/bin/env python3
"""最终稳定版 Task API - 个人资料库 + 多图轮播 + 字幕（修复单图0秒）"""
import json, sqlite3, os, time, subprocess, uuid, shutil, mimetypes, cgi, threading, re
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

DB_PATH = "/home/flybo/clawsjoy/data/tasks.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id TEXT, task_type TEXT,
                  params TEXT, status TEXT, result TEXT, created_at TIMESTAMP, completed_at TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS billing
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, tenant_id TEXT, task_type TEXT,
                  amount REAL, created_at TIMESTAMP)''')
    conn.commit()
    conn.close()

def get_tenant_library_dir(tenant_id):
    base = Path(f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library")
    for sub in ['images', 'videos', 'documents', 'audio', 'thumbnails']:
        (base / sub).mkdir(parents=True, exist_ok=True)
    return base

def get_file_type_category(mime_type):
    if mime_type.startswith('image/'): return 'image'
    elif mime_type.startswith('video/'): return 'video'
    elif mime_type.startswith('audio/'): return 'audio'
    elif mime_type in ['application/pdf', 'text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']: return 'document'
    else: return 'other'

def get_image_size(filepath):
    try:
        from PIL import Image
        with Image.open(filepath) as img: return img.width, img.height
    except: return None, None

def get_video_duration(filepath):
    try:
        result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', filepath],
                                capture_output=True, text=True, timeout=10)
        return float(result.stdout.strip()) if result.stdout else None
    except: return None

def init_library_db(tenant_id):
    db_path = f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, original_name TEXT NOT NULL,
                    storage_path TEXT NOT NULL, file_type TEXT, mime_type TEXT, size INTEGER,
                    width INTEGER, height INTEGER, duration REAL, importance INTEGER DEFAULT 2,
                    auto_tags TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_file_type ON files(file_type)')
    conn.commit()
    conn.close()

def async_tag_file(file_path, file_id, tenant_id):
    name = os.path.splitext(os.path.basename(file_path))[0]
    words = re.findall(r'[\u4e00-\u9fff]+', name)
    tags = words[:3] if words else ["图片"]
    if tags:
        db_path = f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library.db"
        conn = sqlite3.connect(db_path)
        conn.execute("UPDATE files SET auto_tags = ? WHERE id = ?", (','.join(tags), file_id))
        conn.commit()
        conn.close()
        print(f"🏷️ 文件 {file_id} 标签: {tags}")

def get_library_images_by_tags(tenant_id, tags, limit=10):
    db_path = f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library.db"
    if not os.path.exists(db_path):
        return []
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    conditions = ['auto_tags LIKE ?'] * len(tags)
    params = [f'%{t}%' for t in tags]
    query = f"SELECT storage_path FROM files WHERE file_type='image' AND ({' OR '.join(conditions)}) LIMIT {limit}"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def fetch_external_images(city, style, count=6):
    target_dir = f"/home/flybo/clawsjoy/web/images/{city}_{style}_{uuid.uuid4().hex[:6]}"
    os.makedirs(target_dir, exist_ok=True)
    cmd = ['/home/flybo/clawsjoy/bin/spider_unsplash', f"{city} {style}", str(count)]
    subprocess.run(cmd, cwd=target_dir, capture_output=True)
    from glob import glob
    return glob(f"{target_dir}/*.jpg")[:count]


def _call_tts_skill(script, output_path):
    skill_name = os.environ.get("CLAWSJOY_TTS_SKILL", "")
    if not skill_name:
        return False
    skill_dir = f"/home/flybo/clawsjoy/skills/{skill_name}"
    if not os.path.exists(skill_dir):
        print(f"TTS skill {skill_name} 不存在")
        return False
    spec = importlib.util.spec_from_file_location("tts_skill", os.path.join(skill_dir, "main.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    res = module.execute({"script": script, "output_path": output_path})
    return res.get("success", False)

def generate_audio_tts(script, output_path):
    return _call_tts_skill(script, output_path)


class TaskHandler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _record_task(self, tenant_id, task_type, params):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO tasks (tenant_id, task_type, params, status, created_at) VALUES (?,?,?,?,?)",
                  (tenant_id, task_type, json.dumps(params), 'pending', datetime.now().isoformat()))
        task_id = c.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def _update_task(self, task_id, status, result):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE tasks SET status=?, result=?, completed_at=? WHERE id=?", (status, result, datetime.now().isoformat(), task_id))
        conn.commit()
        conn.close()

    def _deduct_balance(self, tenant_id, amount):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO billing (tenant_id, task_type, amount, created_at) VALUES (?,?,?,?)", (tenant_id, 'promo', -amount, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def _get_balance(self, tenant_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT COALESCE(SUM(amount), 0) FROM billing WHERE tenant_id=?", (tenant_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else 0

    def _handle_promo(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            tenant_id = data.get('tenant_id', '1')
            city = data.get('city', '香港')
            style = data.get('style', '科技')
            source = data.get('source', 'auto')

            personal = get_library_images_by_tags(tenant_id, [city], limit=6)
            print(f"🔍 检索到个人图片数: {len(personal)}", flush=True)

            if source == 'library_only':
                final_images = personal[:6]
            elif source == 'external_only':
                final_images = fetch_external_images(city, style, 6)
            else:
                final_images = personal[:]
                if len(final_images) < 6:
                    needed = 6 - len(final_images)
                    final_images.extend(fetch_external_images(city, style, needed))

            if not final_images:
                self.send_json({'success': False, 'error': '没有可用图片素材'})
                return

            task_id = self._record_task(tenant_id, 'promo', {'city': city, 'style': style, 'source': source})
            self._deduct_balance(tenant_id, 0.01)

            script = f"{city} {style} 宣传片，精彩呈现。"
            video_path = f"/home/flybo/clawsjoy/web/videos/{city}_{style}_{int(time.time())}.mp4"
            duration = 15.0

            if len(final_images) == 1:
                first_img = final_images[0]
                cmd = f"ffmpeg -y -loop 1 -i '{first_img}' -c:v libx264 -t {duration} -pix_fmt yuv420p -vf 'scale=1920:1080:force_original_aspect_ratio=1,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,drawtext=text=\"{script}\":fontcolor=white:fontsize=24:x=(w-text_w)/2:y=h-100' '{video_path}'"
                subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL, timeout=60)
            else:
                per_img = duration / len(final_images)
                concat_file = f"/tmp/concat_{int(time.time())}.txt"
                with open(concat_file, 'w') as f:
                    for img in final_images:
                        f.write(f"file '{img}'\n")
                        f.write(f"duration {per_img}\n")
                cmd = f"ffmpeg -y -f concat -safe 0 -i {concat_file} -c:v libx264 -pix_fmt yuv420p -vf 'scale=1920:1080:force_original_aspect_ratio=1,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,drawtext=text=\"{script}\":fontcolor=white:fontsize=24:x=(w-text_w)/2:y=h-100' -t {duration} {video_path}"
                subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL, timeout=60)
                os.remove(concat_file)

            self._update_task(task_id, 'completed', video_path)

            if os.path.exists(video_path):
                self.send_json({
                    'success': True,
                    'video_url': f"/videos/{os.path.basename(video_path)}",
                    'message': f'{city}{style}宣传片已生成',
                    'source': 'library' if personal else 'external',
                    'images_used': len(final_images)
                })
            else:
                self.send_json({'success': False, 'error': '视频合成失败'})
        except Exception as e:
            self.send_json({'success': False, 'error': str(e)}, 500)

    
    def _handle_library_upload(self):
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
        tenant_id = form.getvalue('tenant_id', '1')
        uploaded_file = form['file']
        if not uploaded_file.filename:
            self.send_json({'success': False, 'error': 'No file provided'}, 400)
            return
        file_data = uploaded_file.file.read()
        result = _call_library_skill('upload', {'tenant_id': tenant_id, 'file_data': file_data, 'filename': uploaded_file.filename})
        if result.get('success'):
            self.send_json({'success': True, 'file_id': result['file_id'], 'original_name': uploaded_file.filename})
        else:
            self.send_json({'success': False, 'error': result.get('error', 'Upload failed')})

    
    def _handle_library_list(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        tenant_id = params.get('tenant_id', ['1'])[0]
        file_type = params.get('type', [''])[0]
        limit = int(params.get('limit', [50])[0])
        offset = int(params.get('offset', [0])[0])
        result = _call_library_skill('list', {'tenant_id': tenant_id, 'type': file_type, 'limit': limit, 'offset': offset})
        self.send_json(result)

    def _handle_library_file_request(self, path, query):
        parts = path.split('/')
        if len(parts) < 5:
            self.send_error(400)
            return
        file_id = parts[-1]
        params = parse_qs(query)
        tenant_id = params.get('tenant_id', [''])[0]
        if not tenant_id:
            self.send_error(401, "Missing tenant_id")
            return
        db_path = f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library.db"
        if not os.path.exists(db_path):
            self.send_error(404)
            return
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("SELECT storage_path FROM files WHERE id=?", (file_id,))
        row = c.fetchone()
        conn.close()
        if not row:
            self.send_error(404)
            return
        file_path = row[0]
        expected_prefix = f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library"
        if not file_path.startswith(expected_prefix):
            self.send_error(403)
            return
        if not os.path.exists(file_path):
            self.send_error(404)
            return
        try:
            with open(file_path, 'rb') as f:
                self.send_response(200)
                ext = os.path.splitext(file_path)[1].lower()
                if ext == '.png': self.send_header('Content-Type', 'image/png')
                elif ext in ['.jpg','.jpeg']: self.send_header('Content-Type', 'image/jpeg')
                elif ext == '.mp4': self.send_header('Content-Type', 'video/mp4')
                elif ext == '.pdf': self.send_header('Content-Type', 'application/pdf')
                else: self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Length', os.path.getsize(file_path))
                self.end_headers()
                self.wfile.write(f.read())
        except Exception as e: self.send_error(500, str(e))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/skills":
            self.send_json({"skills": list_skills()})
            return
        parsed = urlparse(self.path)
        if parsed.path == '/api/task/balance':
            params = parse_qs(parsed.query)
            tenant_id = params.get('tenant_id', ['1'])[0]
            balance = self._get_balance(tenant_id)
            self.send_json({'tenant_id': tenant_id, 'balance': balance})
        elif parsed.path == '/api/library/list':
            self._handle_library_list()
        elif parsed.path.startswith('/api/library/file/'):
            self._handle_library_file_request(parsed.path, parsed.query)
        else:
            self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/message":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            skill = load_skill("voice-chat-assistant")
            if skill:
                result = skill.execute(data)
                self.send_json({"reply": result.get("reply", "")})
            else:
                self.send_json({"reply": "语音助手不可用"})
            return
        parsed = urlparse(self.path)
        if parsed.path == '/api/task/promo':
            self._handle_promo()
        elif parsed.path == '/api/library/upload':
            self._handle_library_upload()
        else:
            self.send_error(404)

if __name__ == '__main__':
    init_db()
    port = 8084
    print(f"📋 Task API started: http://redis:{port}")
    print("  POST /api/task/promo - 提交宣传片任务（已修复单图0秒）")
    print("  GET /api/task/balance - 查询余额")
    print("  POST /api/library/upload - 上传文件到个人资料库")
    print("  GET /api/library/list - 列出资料库文件")
    print("  GET /api/library/file/<id>?tenant_id=<tid> - 获取文件")
    HTTPServer(("0.0.0.0", port), TaskHandler).serve_forever()
def _call_library_skill(action, params):
    """调用资料库 Skill"""
    skill_dir = "/home/flybo/clawsjoy/skills/customer-profile-manager"
    if not os.path.exists(skill_dir):
        return {"success": False, "error": "资料库 Skill 未安装"}
    spec = importlib.util.spec_from_file_location("library_skill", os.path.join(skill_dir, "main.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    params['action'] = action
    return module.execute(params)

# 替换原有的 _handle_library_upload, _handle_library_list
# 用以下新版本（通过函数替换，这里用一个简化的方式）
