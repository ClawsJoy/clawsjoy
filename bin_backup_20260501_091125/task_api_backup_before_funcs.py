#!/usr/bin/env python3
"""任务调度器 API - 租户隔离、计费、队列 + 个人资料库管理 + 文件代理"""

import json
import sqlite3
import os
import time
import subprocess
import uuid
import shutil
import mimetypes
import cgi
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ========== 原有配置 ==========
DB_PATH = "/home/flybo/clawsjoy/data/tasks.db"
PROMO_API = "http://localhost:8086/api/promo/make"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  tenant_id TEXT,
                  task_type TEXT,
                  params TEXT,
                  status TEXT,
                  result TEXT,
                  created_at TIMESTAMP,
                  completed_at TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS billing
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  tenant_id TEXT,
                  task_type TEXT,
                  amount REAL,
                  created_at TIMESTAMP)''')
    conn.commit()
    conn.close()

# ========== 个人资料库相关 ==========
def get_tenant_library_dir(tenant_id):
    base = Path(f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library")
    for sub in ['images', 'videos', 'documents', 'audio', 'thumbnails']:
        (base / sub).mkdir(parents=True, exist_ok=True)
    return base

def get_file_type_category(mime_type):
    if mime_type.startswith('image/'):
        return 'image'
    elif mime_type.startswith('video/'):
        return 'video'
    elif mime_type.startswith('audio/'):
        return 'audio'
    elif mime_type in ['application/pdf', 'text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
        return 'document'
    else:
        return 'other'

def get_image_size(filepath):
    try:
        from PIL import Image
        with Image.open(filepath) as img:
            return img.width, img.height
    except:
        return None, None

def get_video_duration(filepath):
    try:
        result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', filepath],
                                capture_output=True, text=True, timeout=10)
        return float(result.stdout.strip()) if result.stdout else None
    except:
        return None

def init_library_db(tenant_id):
    db_path = f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_name TEXT NOT NULL,
                    storage_path TEXT NOT NULL,
                    file_type TEXT,
                    mime_type TEXT,
                    size INTEGER,
                    width INTEGER,
                    height INTEGER,
                    duration REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag_name TEXT UNIQUE NOT NULL,
                    source TEXT DEFAULT 'manual'
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS file_tags (
                    file_id INTEGER,
                    tag_id INTEGER,
                    FOREIGN KEY(file_id) REFERENCES files(id),
                    FOREIGN KEY(tag_id) REFERENCES tags(id),
                    PRIMARY KEY (file_id, tag_id)
                )''')
    c.execute('CREATE INDEX IF NOT EXISTS idx_file_type ON files(file_type)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON files(created_at)')
    conn.commit()
    conn.close()

class TaskHandler(BaseHTTPRequestHandler):
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
        elif parsed.path == '/api/library/upload':
            self._handle_library_upload()
        else:
            self.send_error(404)

    # ========== 原有宣传片处理 ==========
    
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
            video_name = f"{city}_{style}_{int(time.time())}.mp4"
            video_path = f"/home/flybo/clawsjoy/web/videos/{video_name}"
            first_img = final_images[0]
            cmd = f"ffmpeg -y -loop 1 -i '{first_img}' -c:v libx264 -t 15 -pix_fmt yuv420p -vf 'scale=1920:1080' '{video_path}'"
            subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL)
            self._update_task(task_id, 'completed', video_path)
            if os.path.exists(video_path):
                self.send_json({
                    'success': True,
                    'video_url': f"/videos/{video_name}",
                    'message': f'{city}{style}宣传片已生成',
                    'source': 'library' if personal else 'external',
                    'images_used': len(final_images)
                })
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
        sub_dir = category + 's' if category in ['image', 'video', 'audio', 'document'] else 'others'
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
        
        self.send_json({
            'success': True,
            'file_id': file_id,
            'original_name': uploaded_file.filename,
            'type': category,
            'size': size
        })

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
        # 提取 file_id
        parts = path.split('/')
        if len(parts) < 5:
            self.send_error(400)
            return
        file_id = parts[-1]
        
        # 获取 tenant_id 参数
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
                if ext in ['.png']:
                    self.send_header('Content-Type', 'image/png')
                elif ext in ['.jpg', '.jpeg']:
                    self.send_header('Content-Type', 'image/jpeg')
                elif ext in ['.mp4']:
                    self.send_header('Content-Type', 'video/mp4')
                elif ext in ['.pdf']:
                    self.send_header('Content-Type', 'application/pdf')
                else:
                    self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Length', os.path.getsize(file_path))
                self.end_headers()
                self.wfile.write(f.read())
        except Exception as e:
            self.send_error(500, str(e))

    # ========== 辅助方法 ==========
    def _record_task(self, tenant_id, task_type, params):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO tasks (tenant_id, task_type, params, status, created_at)
                     VALUES (?, ?, ?, ?, ?)''',
                  (tenant_id, task_type, json.dumps(params), 'pending', datetime.now().isoformat()))
        task_id = c.lastrowid
        conn.commit()
        conn.close()
        return task_id

    def _update_task(self, task_id, status, result):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''UPDATE tasks SET status=?, result=?, completed_at=?
                     WHERE id=?''',
                  (status, result, datetime.now().isoformat(), task_id))
        conn.commit()
        conn.close()

    def _deduct_balance(self, tenant_id, amount):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO billing (tenant_id, task_type, amount, created_at)
                     VALUES (?, ?, ?, ?)''',
                  (tenant_id, 'promo', -amount, datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def _get_balance(self, tenant_id):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT COALESCE(SUM(amount), 0) FROM billing WHERE tenant_id=?', (tenant_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else 0

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def log_message(self, format, *args):
        print(f"[{datetime.now().isoformat()}] {format % args}")

if __name__ == '__main__':
    init_db()
    port = 8084
    print(f"📋 Task API started: http://localhost:{port}")
    print(f"  POST /api/task/promo - 提交宣传片任务")
    print(f"  GET /api/task/balance - 查询余额")
    print(f"  POST /api/library/upload - 上传文件到个人资料库")
    print(f"  GET /api/library/list - 列出资料库文件")
    print(f"  GET /api/library/file/<id>?tenant_id=<tid> - 获取文件")
    HTTPServer(("0.0.0.0", port), TaskHandler).serve_forever()

def get_library_images_by_tags(tenant_id, tags, limit=10):
    """从租户资料库检索匹配标签的图片路径"""
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
