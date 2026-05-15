from error_utils import send_json_response, send_error, send_success
#!/usr/bin/env python3
"""ClawsJoy 认证服务 - 支持邮箱验证和密码重置"""

import json
import sqlite3
import hashlib
import jwt
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from itsdangerous import URLSafeTimedSerializer

# ============ 配置 ============
SECRET_KEY = os.environ.get('SECRET_KEY', 'clawsjoy-secret-2026')
DB_PATH = "/mnt/d/clawsjoy/data/auth.db"
TOKEN_EXPIRY_DAYS = 7

# 邮件配置
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.qq.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASS = os.environ.get('SMTP_PASS', '')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:8082')

serializer = URLSafeTimedSerializer(SECRET_KEY)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(email):
    return serializer.dumps(email, salt='email-verify')

def verify_token(token, expiration=3600):
    try:
        return serializer.loads(token, salt='email-verify', max_age=expiration)
    except:
        return None

def send_email(to_email, subject, html_body):
    if not SMTP_USER or not SMTP_PASS:
        print("邮件未配置，跳过发送")
        return False
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_body, 'html', 'utf-8'))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False

def init_db():
    Path("/mnt/d/clawsjoy/data").mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT,
        tenant_id TEXT,
        role TEXT,
        email_verified INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        pwd = hash_password("admin123")
        c.execute("INSERT INTO users (username, password, tenant_id, role, email_verified) VALUES (?,?,?,?,?)",
                  ("admin", pwd, "0", "admin", 1))
        conn.commit()
    conn.close()

def generate_jwt(username, tenant_id, role):
    payload = {
        "username": username,
        "tenant_id": tenant_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=TOKEN_EXPIRY_DAYS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

class AuthHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/api/auth/health':
            self.send_json({"status": "ok"})
        elif parsed.path == '/api/auth/verify':
            params = parse_qs(parsed.query)
            token = params.get('token', [''])[0]
            email = verify_token(token)
            if email:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("UPDATE users SET email_verified=1 WHERE email=?", (email,))
                conn.commit()
                conn.close()
                send_success(self, None, "邮箱验证成功，请登录")
            else:
                send_error(self, "BAD_REQUEST", "链接已失效")
        else:
            self.send_error(404)
    
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(length))
        
        if self.path == '/api/auth/login':
            self._handle_login(data)
        elif self.path == '/api/auth/register':
            self._handle_register(data)
        elif self.path == '/api/auth/forgot':
            self._handle_forgot(data)
        elif self.path == '/api/auth/reset':
            self._handle_reset(data)
        else:
            self.send_error(404)
    
    def _handle_login(self, data):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT username, tenant_id, role, email_verified FROM users WHERE username=? AND password=?",
                  (data.get('username'), hash_password(data.get('password', ''))))
        user = c.fetchone()
        conn.close()
        if user:
            if user[3] == 0:
                self.send_json({"success": False, "error": "请先验证邮箱"}, 401)
                return
            token = generate_jwt(user[0], user[1], user[2])
            send_success(self, {"token": token, "user": {"name": user[0], "tenant_id": user[1], "role": user[2]}}, "登录成功")
        else:
            send_error(self, "UNAUTHORIZED", "用户名或密码错误")
    
    def _handle_register(self, data):
        email = data.get('email')
        if not email:
            send_error(self, "VALIDATION_ERROR", "邮箱必填")
            return
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password, email, tenant_id, role) VALUES (?,?,?,?,?)",
                      (data.get('username'), hash_password(data.get('password', '')), email, data.get('tenant_id', '1'), 'user'))
            conn.commit()
            
            # 发送验证邮件
            token = generate_token(email)
            verify_url = f"{FRONTEND_URL}/api/auth/verify?token={token}"
            html = f"<h2>欢迎注册 ClawsJoy</h2><p>请点击链接验证邮箱：<a href='{verify_url}'>{verify_url}</a></p><p>链接有效期1小时</p>"
            send_email(email, 'ClawsJoy 邮箱验证', html)
            
            send_success(self, None, "注册成功，请查收验证邮件")
        except Exception as e:
            send_error(self, "BAD_REQUEST", str(e))
        finally:
            conn.close()
    
    def _handle_forgot(self, data):
        email = data.get('email')
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE email=?", (email,))
        if c.fetchone():
            token = generate_token(email)
            reset_url = f"{FRONTEND_URL}/reset-password?token={token}"
            html = f"<h2>重置 ClawsJoy 密码</h2><p>请点击链接重置密码：<a href='{reset_url}'>{reset_url}</a></p><p>链接有效期1小时</p>"
            send_email(email, 'ClawsJoy 密码重置', html)
            send_success(self, None, "重置邮件已发送")
        else:
            send_error(self, "NOT_FOUND", "邮箱未注册")
        conn.close()
    
    def _handle_reset(self, data):
        token = data.get('token')
        new_password = data.get('new_password')
        email = verify_token(token)
        if not email:
            send_error(self, "BAD_REQUEST", "链接已失效")
            return
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET password=? WHERE email=?", (hash_password(new_password), email))
        conn.commit()
        conn.close()
        send_success(self, None, "密码重置成功")
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def log_message(self, *args): pass

if __name__ == "__main__":
    init_db()
    port = 8092
    print(f"🔐 Auth API: http://localhost:{port}")
    print(f"   POST /api/auth/login")
    print(f"   POST /api/auth/register")
    print(f"   POST /api/auth/forgot")
    print(f"   POST /api/auth/reset")
    print(f"   GET  /api/auth/verify")
    HTTPServer(("0.0.0.0", port), AuthHandler).serve_forever()

# 错误处理装饰器（可选，不影响现有逻辑）
def safe_handler(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())
    return wrapper
