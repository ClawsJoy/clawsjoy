"""WebSocket 实时推送服务 - 使用现有认证"""

import time
import sqlite3
from datetime import datetime
from pathlib import Path
from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

# 导入现有认证模块
from lib.auth_api import auth_manager

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 数据库初始化
DB_PATH = Path(__file__).parent.parent / "data/websocket.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS connections (
            sid TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            username TEXT,
            room TEXT,
            connected_at TIMESTAMP,
            last_active TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS offline_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            event TEXT NOT NULL,
            data TEXT,
            created_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def save_offline_message(user_id: str, event: str, data: dict):
    import json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO offline_messages (user_id, event, data) VALUES (?, ?, ?)",
        (user_id, event, json.dumps(data))
    )
    conn.commit()
    conn.close()

def get_offline_messages(user_id: str):
    import json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT event, data FROM offline_messages WHERE user_id = ? ORDER BY id",
        (user_id,)
    )
    rows = c.fetchall()
    c.execute("DELETE FROM offline_messages WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return [{'event': r[0], 'data': json.loads(r[1])} for r in rows]


# ========== WebSocket 事件 ==========

@socketio.on('connect')
def handle_connect():
    print(f"✅ 客户端连接: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM connections WHERE sid = ?", (request.sid,))
    conn.commit()
    conn.close()
    print(f"❌ 客户端断开: {request.sid}")

@socketio.on('auth')
def handle_auth(data):
    """认证 - 使用现有 auth_manager"""
    token = data.get('token', '')
    
    # 使用现有认证验证 token
    payload = auth_manager.verify_token(token)
    
    if not payload:
        emit('auth_error', {'error': 'Invalid token'})
        return
    
    user_id = payload.get('user_id')
    username = payload.get('username', user_id)
    room = f"user_{user_id}"
    join_room(room)
    
    # 记录连接
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO connections (sid, user_id, username, room, connected_at, last_active) VALUES (?, ?, ?, ?, ?, ?)",
        (request.sid, user_id, username, room, datetime.now().isoformat(), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    
    # 发送离线消息
    offline = get_offline_messages(user_id)
    for msg in offline:
        emit(msg['event'], msg['data'], room=request.sid)
    
    emit('auth_success', {
        'user_id': user_id,
        'username': username,
        'offline_count': len(offline)
    })
    print(f"🔐 用户认证成功: {username} ({user_id})")

@socketio.on('join')
def handle_join(data):
    user_id = data.get('user_id', '')
    room = f"user_{user_id}"
    join_room(room)
    emit('joined', {'room': room})

@socketio.on('chat_message')
def handle_chat_message(data):
    user_id = data.get('user_id', '')
    message = data.get('message', '')
    room = f"user_{user_id}"
    emit('chat_response', {
        'user_id': user_id,
        'message': message,
        'timestamp': time.time()
    }, room=room, include_self=False)


# ========== 推送函数 ==========

def push_to_user(user_id: str, event: str, data: dict):
    import json
    room = f"user_{user_id}"
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT sid FROM connections WHERE user_id = ?", (user_id,))
    online = c.fetchone()
    conn.close()
    
    if online:
        socketio.emit(event, data, room=room)
        print(f"📤 推送到用户 {user_id}: {event}")
    else:
        save_offline_message(user_id, event, data)
        print(f"💾 用户 {user_id} 离线，消息已保存")

def push_streaming(user_id: str, chunk: str):
    push_to_user(user_id, 'stream_chunk', {'chunk': chunk, 'timestamp': time.time()})

def push_progress(user_id: str, task_id: str, progress: int, message: str = ""):
    push_to_user(user_id, 'task_progress', {
        'task_id': task_id,
        'progress': progress,
        'message': message,
        'timestamp': time.time()
    })

def push_notification(user_id: str, title: str, body: str, level: str = "info"):
    push_to_user(user_id, 'notification', {
        'title': title,
        'body': body,
        'level': level,
        'timestamp': time.time()
    })


if __name__ == '__main__':
    print("=" * 50)
    print("🔌 ClawsJoy WebSocket 中间件")
    print("   地址: ws://localhost:5003")
    print("   认证: 使用现有 JWT token")
    print("=" * 50)
    socketio.run(app, host='0.0.0.0', port=5003, debug=False)
