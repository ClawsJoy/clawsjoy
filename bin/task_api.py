#!/usr/bin/env python3
"""任务调度器 - 集成记忆服务和引擎路由"""

import json, sqlite3, os, time, subprocess, uuid, shutil, mimetypes, cgi, threading, re
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# 添加引擎路由和记忆服务
import sys
sys.path.insert(0, '/mnt/d/clawsjoy/bin')
sys.path.insert(0, '/mnt/d/clawsjoy/skills/memory')

from executor_adapter import ExecutorRouterWithConfig
from execute import execute as memory_execute

sys.path.insert(0, "/mnt/d/clawsjoy/skills/memory")
from execute import execute as memory_execute

from memory_service import get_memory_service
#!/usr/bin/env python3
"""完整版 task_api - 多图轮播 + TTS 音频 + 字幕"""
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
    try:
        import subprocess
        cmd = f"edge-tts --text '{script}' --voice zh-CN-XiaoxiaoNeural --write-media '{output_path}'"
        subprocess.run(cmd, shell=True, check=True, timeout=30)
        return True
    except Exception as e:
        print(f"TTS 失败: {e}", flush=True)
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
            # 转发到 promo_api (8086)
            import requests
            resp = requests.post('http://redis:8086/api/promo/make', 
                                json={'city': city, 'style': style},
                                timeout=60)
            result = resp.json()
            if result.get('success'):
                self.send_json({
                    'success': True,
                    'video_url': result.get('video_url'),
                    'message': f'{city}{style}宣传片已生成'
                })
            else:
                self.send_json({'success': False, 'error': result.get('error', '生成失败')})
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

    def _handle_editor_save(self):
        """保存编辑后的图片"""
        import uuid
        import cgi
        from PIL import Image
        from pathlib import Path
        try:
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                     environ={'REQUEST_METHOD': 'POST'})
            tenant_id = form.getvalue('tenant_id', '1')
            image_file = form['image']]
            if not image_file or not image_file.file:
                self.send_json({'success': False, 'error': 'No image file'}, 400)
                return
            temp_path = f"/tmp/editor_{uuid.uuid4().hex}.jpg"
            with open(temp_path, 'wb') as f:
                f.write(image_file.file.read())
            img = Image.open(temp_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            tenant_lib = Path(f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library/images")
            tenant_lib.mkdir(parents=True, exist_ok=True)
            final_name = f"{uuid.uuid4().hex}.jpg"
            final_path = tenant_lib / final_name
            img.save(final_path, 'JPEG', quality=90)
            db_path = f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library.db"
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute('''
                INSERT INTO files (original_name, storage_path, file_type, mime_type, size, width, height, edited)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (f"edited_{final_name}", str(final_path), 'image', 'image/jpeg',
                  os.path.getsize(final_path), img.width, img.height, 1))
            file_id = c.lastrowid
            conn.commit()
            conn.close()
            os.unlink(temp_path)
            self.send_json({
                'success': True,
                'file_id': file_id,
                'url': f'/videos/{final_name}',
                'message': '保存成功'
            })
        except Exception as e:
            print(f"编辑器保存失败: {e}")
            self.send_json({'success': False, 'error': str(e)}, 500)

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

    def _handle_chat_with_memory(self, data):
        return {"success": True, "message": "ok"}

    def _handle_switch_engine(self, data):
        return {"success": True}

    def _handle_list_engines(self):
        return {"success": True, "engines": []}

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/chat":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            result = self._handle_chat_with_memory(data)
            self.send_json(result)
            return
        elif parsed.path == "/api/switch_engine":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            result = self._handle_switch_engine(data)
            self.send_json(result)
            return
        elif parsed.path == "/api/list_engines":
            result = self._handle_list_engines()
            self.send_json(result)
            return

        parsed = urlparse(self.path)
        if parsed.path == '/api/task/promo':
            self._handle_promo()
        elif parsed.path == '/api/library/upload':
            self._handle_library_upload()
        elif parsed.path == '/api/library/editor/save':
            self._handle_editor_save()
        else:
            self.send_error(404)

if __name__ == '__main__':
    init_db()
    port = 8084
    print(f"📋 Task API started: http://redis:{port}")
    HTTPServer(("0.0.0.0", port), TaskHandler).serve_forever()

# ========== 图片编辑器 API ==========
def _handle_editor_save(self):
    """保存编辑后的图片"""
    import uuid
    from PIL import Image
    try:
        # 解析 multipart 数据
        import cgi
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                 environ={'REQUEST_METHOD': 'POST'})
        tenant_id = form.getvalue('tenant_id', '1')
        original_id = form.getvalue('original_id', '')
        image_file = form['image']
        if not image_file or not image_file.file:
            self.send_json({'success': False, 'error': 'No image file'}, 400)
            return
        # 保存临时文件
        temp_path = f"/tmp/editor_{uuid.uuid4().hex}.jpg"
        with open(temp_path, 'wb') as f:
            f.write(image_file.file.read())
        # 用 PIL 优化
        img = Image.open(temp_path)
        # 确保是 RGB 模式
        if img.mode != 'RGB':
            img = img.convert('RGB')
        # 保存到租户资料库
        tenant_lib = Path(f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library/images")
        tenant_lib.mkdir(parents=True, exist_ok=True)
        final_name = f"{uuid.uuid4().hex}.jpg"
        final_path = tenant_lib / final_name
        img.save(final_path, 'JPEG', quality=90, optimize=True)
        # 记录到数据库
        db_path = f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library.db"
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO files (original_name, storage_path, file_type, mime_type, size, width, height, edited)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (f"edited_{final_name}", str(final_path), 'image', 'image/jpeg',
              os.path.getsize(final_path), img.width, img.height, 1))
        file_id = c.lastrowid
        conn.commit()
        conn.close()
        # 清理临时文件
        os.unlink(temp_path)
        self.send_json({
            'success': True,
            'file_id': file_id,
            'url': f'/videos/{final_name}',
            'message': '保存成功'
        })
    except Exception as e:
        print(f"编辑器保存失败: {e}")
        self.send_json({'success': False, 'error': str(e)}, 500)

# 在 do_POST 中添加路由
# 找到 do_POST 方法，添加 elif
# 由于修改复杂，建议手动添加，或执行下面的 sed

# ========== 图片编辑器 API ==========
def _handle_editor_save(self):
    """保存编辑后的图片"""
    import uuid
    from PIL import Image
    try:
        # 解析 multipart 数据
        import cgi
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                 environ={'REQUEST_METHOD': 'POST'})
        tenant_id = form.getvalue('tenant_id', '1')
        image_file = form.get('image')
        if not image_file or not image_file.file:
            self.send_json({'success': False, 'error': 'No image file'}, 400)
            return
        # 保存临时文件
        temp_path = f"/tmp/editor_{uuid.uuid4().hex}.jpg"
        with open(temp_path, 'wb') as f:
            f.write(image_file.file.read())
        # 用 PIL 优化
        img = Image.open(temp_path)
        # 确保是 RGB 模式
        if img.mode != 'RGB':
            img = img.convert('RGB')
        # 保存到租户资料库
        tenant_lib = Path(f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library/images")
        tenant_lib.mkdir(parents=True, exist_ok=True)
        final_name = f"{uuid.uuid4().hex}.jpg"
        final_path = tenant_lib / final_name
        img.save(final_path, 'JPEG', quality=90, optimize=True)
        # 记录到数据库
        db_path = f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library.db"
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO files (original_name, storage_path, file_type, mime_type, size, width, height, edited)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (f"edited_{final_name}", str(final_path), 'image', 'image/jpeg',
              os.path.getsize(final_path), img.width, img.height, 1))
        file_id = c.lastrowid
        conn.commit()
        conn.close()
        # 清理临时文件
        os.unlink(temp_path)
        self.send_json({
            'success': True,
            'file_id': file_id,
            'url': f'/videos/{final_name}',
            'message': '保存成功'
        })
    except Exception as e:
        print(f"编辑器保存失败: {e}")
        self.send_json({'success': False, 'error': str(e)}, 500)


    def _handle_editor_save(self):
        """保存编辑后的图片"""
        import uuid
        import cgi
        from PIL import Image
        from pathlib import Path
        try:
            form = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                     environ={'REQUEST_METHOD': 'POST'})
            tenant_id = form.getvalue('tenant_id', '1')
            image_file = form['image']
            if not image_file or not image_file.file:
                self.send_json({'success': False, 'error': 'No image file'}, 400)
                return
            # 保存临时文件
            temp_path = f"/tmp/editor_{uuid.uuid4().hex}.jpg"
            with open(temp_path, 'wb') as f:
                f.write(image_file.file.read())
            # 用 PIL 处理
            img = Image.open(temp_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # 保存到租户资料库
            tenant_lib = Path(f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library/images")
            tenant_lib.mkdir(parents=True, exist_ok=True)
            final_name = f"{uuid.uuid4().hex}.jpg"
            final_path = tenant_lib / final_name
            img.save(final_path, 'JPEG', quality=90)
            # 记录到数据库
            db_path = f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library.db"
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute('''
                INSERT INTO files (original_name, storage_path, file_type, mime_type, size, width, height, edited)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (f"edited_{final_name}", str(final_path), 'image', 'image/jpeg',
                  os.path.getsize(final_path), img.width, img.height, 1))
            file_id = c.lastrowid
            conn.commit()
            conn.close()
            os.unlink(temp_path)
            self.send_json({
                'success': True,
                'file_id': file_id,
                'url': f'/videos/{final_name}',
                'message': '保存成功'
            })
        except Exception as e:
            print(f"编辑器保存失败: {e}")
            self.send_json({'success': False, 'error': str(e)}, 500)


    def _handle_chat_with_memory(self, data):
        """带记忆和引擎路由的聊天处理"""
        tenant_id = data.get('tenant_id', '1')
        session_id = data.get('session_id', 'default')
        message = data.get('message', '')
        
        # 1. 获取历史记忆
        memories = memory_execute({
            'action': 'get',
            'tenant_id': tenant_id,
            'session_id': session_id,
            'limit': 5
        })
        
        # 2. 构建上下文
        context = ""
        if memories.get('success') and memories.get('memories'):
            context = "历史对话:\n"
            for m in memories['memories']:
                context += f"{m['role']}: {m['content']}\n"
            context += f"\n当前用户: {message}\n"
        else:
            context = message
        
        # 3. 通过引擎路由执行任务
        router = ExecutorRouterWithConfig()
        result = router.route({
            'prompt': context,
            'task_type': data.get('task_type', 'general')
        })
        
        # 4. 保存新记忆
        memory_execute({
            'action': 'add',
            'tenant_id': tenant_id,
            'session_id': session_id,
            'role': 'user',
            'content': message
        })
        
        if result.get('success'):
            memory_execute({
                'action': 'add',
                'tenant_id': tenant_id,
                'session_id': session_id,
                'role': 'assistant',
                'content': result.get('output', '')
            })
            return result
        
        return {'success': False, 'error': 'No engine available'}


    def _handle_switch_engine(self, data):
        """切换执行引擎"""
        engine = data.get('engine', 'openclaw')
        config_path = "/mnt/d/clawsjoy/config/engine.json"
        
        with open(config_path, 'w') as f:
            json.dump({
                'executor': engine,
                'fallback': 'self',
                'updated_at': datetime.now().isoformat()
            }, f)
        
        return {'success': True, 'engine': engine, 'message': f'已切换到 {engine} 引擎'}

    def _handle_list_engines(self):
        """列出可用引擎"""
        router = ExecutorRouterWithConfig()
        return {
            'success': True,
            'current': router.config.get('executor', 'openclaw'),
            'engines': router.list_engines()
        }


    def _handle_chat_with_memory(self, data):
        """带记忆的聊天处理"""
        tenant_id = data.get('tenant_id', '1')
        session_id = data.get('session_id', 'default')
        message = data.get('message', '')
        
        # 简单响应
        return {'success': True, 'type': 'text', 'message': f'收到消息: {message}'}
    
    def _handle_switch_engine(self, data):
        """切换引擎"""
        engine = data.get('engine', 'openclaw')
        return {'success': True, 'engine': engine}
    
    def _handle_list_engines(self):
        """列出引擎"""
        return {'success': True, 'engines': ['openclaw', 'claude_code', 'self']}

