#!/usr/bin/env python3
"""完整稳定版 Task API - 资料库 + 宣传片 + 聊天路由"""
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

def generate_audio_tts(script, output_path):
    return False

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
            print(f"🔍 个人图片数: {len(personal)}", flush=True)
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
            task_id = self._record_task(tenant_id, 'promo', {'city': city, 'style': style})
            self._deduct_balance(tenant_id, 0.01)
            script = f"{city} {style} 宣传片，精彩呈现。"
            video_path = f"/home/flybo/clawsjoy/web/videos/{city}_{style}_{int(time.time())}.mp4"
            duration = 15.0
            if len(final_images) == 1:
                img = final_images[0]
                cmd = f"ffmpeg -y -loop 1 -i '{img}' -c:v libx264 -t {duration} -pix_fmt yuv420p -vf 'scale=1920:1080:force_original_aspect_ratio=1,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,drawtext=text=\"{script}\":fontcolor=white:fontsize=24:x=(w-text_w)/2:y=h-100' '{video_path}'"
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
                self.send_json({'success': True, 'video_url': f"/videos/{os.path.basename(video_path)}", 'message': f'{city}{style}宣传片已生成'})
            else:
                self.send_json({'success': False, 'error': '视频合成失败'})
        except Exception as e:
            self.send_json({'success': False, 'error': str(e)}, 500)

    def _handle_library_upload(self):
        content_type = self.headers.get('Content-Type')
        if not content_type or not content_type.startswith('multipart/form-data'):
            self.send_json({'success': False, 'error': 'Invalid content type'}, 400)
            return
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})
        tenant_id = form.getvalue('tenant_id', '1')
        uploaded_file = form['file']
        if not uploaded_file.filename:
            self.send_json({'success': False, 'error': 'No file provided'}, 400)
            return
        init_library_db(tenant_id)
        mime_type = uploaded_file.type or mimetypes.guess_type(uploaded_file.filename)[0] or 'application/octet-stream'
        category = get_file_type_category(mime_type)
        sub_dir = category + 's' if category in ['image','video','audio','document'] else 'others'
        tenant_lib = get_tenant_library_dir(tenant_id)
        target_dir = tenant_lib / sub_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        ext = os.path.splitext(uploaded_file.filename)[1]
        new_name = f"{uuid.uuid4().hex}{ext}"
        target_path = target_dir / new_name
        with open(target_path, 'wb') as f:
            f.write(uploaded_file.file.read())
        size = os.path.getsize(target_path)
        width = height = duration = None
        if category == 'image':
            width, height = get_image_size(target_path)
        elif category == 'video':
            duration = get_video_duration(target_path)
        db_path = f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library.db"
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''INSERT INTO files (original_name, storage_path, file_type, mime_type, size, width, height, duration)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (uploaded_file.filename, str(target_path), category, mime_type, size, width, height, duration))
        file_id = c.lastrowid
        conn.commit()
        conn.close()
        threading.Thread(target=async_tag_file, args=(str(target_path), file_id, tenant_id)).start()
        self.send_json({'success': True, 'file_id': file_id, 'original_name': uploaded_file.filename})

    def _handle_library_list(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        tenant_id = params.get('tenant_id', ['1'])[0]
        file_type = params.get('type', [''])[0]
        limit = int(params.get('limit', [50])[0])
        offset = int(params.get('offset', [0])[0])
        db_path = f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library.db"
        if not os.path.exists(db_path):
            self.send_json({'success': True, 'files': [], 'total': 0})
            return
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        query = "SELECT id, original_name, storage_path, file_type, size, created_at FROM files WHERE 1=1"
        args = []
        if file_type:
            query += " AND file_type = ?"
            args.append(file_type)
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        args.extend([limit, offset])
        c.execute(query, args)
        rows = c.fetchall()
        conn.close()
        files = [{'id': r[0], 'name': r[1], 'path': r[2], 'type': r[3], 'size': r[4], 'created_at': r[5]} for r in rows]
        self.send_json({'success': True, 'files': files, 'total': len(files)})

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
                else: self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Length', os.path.getsize(file_path))
                self.end_headers()
                self.wfile.write(f.read())
        except Exception as e: self.send_error(500, str(e))

    
    
    def _handle_chat(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            tenant_id = data.get('tenant_id', '1')
            message = data.get('message', '')
            session_id = data.get('session_id', 'default')
            
            # 调用语音聊天 Skill
            skill_dir = "/home/flybo/clawsjoy/skills/voice-chat-assistant"
            if os.path.exists(skill_dir):
                try:
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("chat_skill", os.path.join(skill_dir, "main.py"))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    result = module.execute({"tenant_id": tenant_id, "message": message, "session_id": session_id})
                    print(f"DEBUG: Skill 返回结果: {result}", flush=True)
                    if result and result.get("success"):
                        self.send_json(result.get("response", {}))
                        return
                except Exception as e:
                    print(f"Chat Skill 调用失败: {e}", flush=True)
            
            # 降级响应
            self.send_json({"type": "text", "message": f"收到消息: {message}，我是 ClawsJoy 助手。"})
        except Exception as e:
            self.send_json({"type": "text", "message": f"处理失败: {str(e)}"})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
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
        if parsed.path == '/api/task/promo':
            self._handle_promo()
        elif parsed.path == '/api/chat':
            self._handle_chat()
        elif parsed.path == '/api/library/upload':
            self._handle_library_upload()
        else:
            self.send_error(404)

if __name__ == '__main__':
    init_db()
    port = 8084
    print(f"📋 Task API started: http://redis:{port}")
    HTTPServer(("0.0.0.0", port), TaskHandler).serve_forever()
    def _execute_action(self, action_data):
        action = action_data.get('action')
        if action == 'make_promo':
            # 直接调用宣传片生成
            self._handle_promo_from_data(action_data)
        elif action == 'list_library':
            # 调用资料库列表
            tenant_id = action_data.get('tenant_id', '1')
            limit = action_data.get('limit', 10)
            db_path = f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library.db"
            if not os.path.exists(db_path):
                self.send_json({'type': 'text', 'message': '资料库为空'})
                return
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute("SELECT original_name, storage_path, file_type FROM files ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = c.fetchall()
            conn.close()
            if rows:
                files = [{'name': r[0], 'path': r[1], 'type': r[2]} for r in rows]
                self.send_json({'type': 'library', 'files': files})
            else:
                self.send_json({'type': 'text', 'message': '资料库暂无文件'})
        elif action == 'chat':
            self.send_json({'type': 'text', 'message': action_data.get('message', '')})
        else:
            self.send_json({'type': 'text', 'message': '未知动作'})

    def _handle_promo_from_data(self, data):
        """从动作数据生成宣传片"""
        tenant_id = data.get('tenant_id', '1')
        city = data.get('city', '香港')
        style = data.get('style', '科技')
        # 临时构造一个类似请求的数据
        class DummyRequest:
            pass
        old_rfile = self.rfile
        self.rfile = type('obj', (object,), {'read': lambda s, x: json.dumps({'tenant_id': tenant_id, 'city': city, 'style': style}).encode()})()
        self.headers = type('obj', (object,), {'get': lambda s, x: str(len(json.dumps({'tenant_id': tenant_id, 'city': city, 'style': style})))})()
        self._handle_promo()
        self.rfile = old_rfile
