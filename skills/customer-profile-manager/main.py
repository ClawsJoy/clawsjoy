import sqlite3, os, re, uuid, threading, mimetypes
from pathlib import Path
from datetime import datetime

def get_tenant_library_dir(tenant_id):
    base = Path(f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library")
    for sub in ['images', 'videos', 'documents', 'audio', 'thumbnails']:
        (base / sub).mkdir(parents=True, exist_ok=True)
    return base

def get_file_type_category(mime_type):
    if mime_type.startswith('image/'): return 'image'
    elif mime_type.startswith('video/'): return 'video'
    elif mime_type.startswith('audio/'): return 'audio'
    else: return 'other'

def get_image_size(filepath):
    try:
        from PIL import Image
        with Image.open(filepath) as img: return img.width, img.height
    except: return None, None

def init_library_db(tenant_id):
    db_path = f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, original_name TEXT NOT NULL,
                    storage_path TEXT NOT NULL, file_type TEXT, mime_type TEXT, size INTEGER,
                    width INTEGER, height INTEGER, duration REAL, importance INTEGER DEFAULT 2,
                    auto_tags TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
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

def upload_file(tenant_id, file_data, filename):
    init_library_db(tenant_id)
    mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    category = get_file_type_category(mime_type)
    sub_dir = category + 's'
    tenant_lib = get_tenant_library_dir(tenant_id)
    target_dir = tenant_lib / sub_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    ext = os.path.splitext(filename)[1]
    new_name = f"{uuid.uuid4().hex}{ext}"
    target_path = target_dir / new_name
    with open(target_path, 'wb') as f:
        f.write(file_data)
    size = os.path.getsize(target_path)
    width = height = None
    if category == 'image':
        width, height = get_image_size(target_path)
    db_path = f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library.db"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''INSERT INTO files (original_name, storage_path, file_type, mime_type, size, width, height)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (filename, str(target_path), category, mime_type, size, width, height))
    file_id = c.lastrowid
    conn.commit()
    conn.close()
    threading.Thread(target=async_tag_file, args=(str(target_path), file_id, tenant_id)).start()
    return file_id

def list_files(tenant_id, file_type=None, limit=50, offset=0):
    db_path = f"/home/flybo/clawsjoy/tenants/tenant_{tenant_id}/library.db"
    if not os.path.exists(db_path):
        return []
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
    return [{'id': r[0], 'name': r[1], 'path': r[2], 'type': r[3], 'size': r[4], 'created_at': r[5]} for r in rows]

def execute(params):
    action = params.get('action')
    tenant_id = params.get('tenant_id', '1')
    if action == 'upload':
        file_id = upload_file(tenant_id, params['file_data'], params['filename'])
        return {'success': True, 'file_id': file_id}
    elif action == 'list':
        files = list_files(tenant_id, params.get('type'), params.get('limit', 50), params.get('offset', 0))
        return {'success': True, 'files': files, 'total': len(files)}
    else:
        return {'success': False, 'error': f'Unknown action: {action}'}
