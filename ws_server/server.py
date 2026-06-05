"""WebSocket 实时推送服务 - 使用现有认证"""

import sqlite3
import time
from datetime import datetime
from pathlib import Path

from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# 数据库初始化
DB_PATH = Path(__file__).parent.parent / "data/websocket.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS connections (
            sid TEXT PRIMARY KEY,
            user_id TEXT,
            room TEXT,
            connected_at TIMESTAMP,
            last_active TIMESTAMP
        )
    """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room TEXT,
            user_id TEXT,
            message TEXT,
            timestamp TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()


def get_auth_manager():
    """延迟导入 auth_manager，避免循环导入"""
    from lib.auth_api import auth_manager
    return auth_manager


@socketio.on('connect')
def handle_connect():
    """处理客户端连接"""
    sid = request.sid
    
    # 从请求参数获取 token
    token = request.args.get('token')
    
    if token:
        auth_manager = get_auth_manager()
        user_id = auth_manager.verify_token(token)
        if user_id:
            # 记录连接
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                "INSERT OR REPLACE INTO connections (sid, user_id, connected_at, last_active) VALUES (?, ?, ?, ?)",
                (sid, user_id, datetime.now(), datetime.now())
            )
            conn.commit()
            conn.close()
            
            emit('connected', {'status': 'success', 'user_id': user_id})
            return
    
    # 未认证连接
    emit('connected', {'status': 'error', 'message': '认证失败'})


@socketio.on('join')
def handle_join(data):
    """加入房间"""
    room = data.get('room')
    if not room:
        emit('error', {'message': '房间名不能为空'})
        return
    
    join_room(room)
    
    # 更新数据库中的房间
    sid = request.sid
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE connections SET room = ?, last_active = ? WHERE sid = ?", (room, datetime.now(), sid))
    conn.commit()
    conn.close()
    
    emit('joined', {'room': room}, room=room)


@socketio.on('message')
def handle_message(data):
    """处理消息"""
    room = data.get('room')
    message = data.get('message')
    user_id = data.get('user_id')
    
    if not room or not message:
        emit('error', {'message': '缺少必要参数'})
        return
    
    # 保存消息到数据库
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO messages (room, user_id, message, timestamp) VALUES (?, ?, ?, ?)",
        (room, user_id, message, datetime.now())
    )
    conn.commit()
    conn.close()
    
    # 广播消息到房间
    emit('message', {
        'user_id': user_id,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }, room=room)


@socketio.on('leave')
def handle_leave(data):
    """离开房间"""
    room = data.get('room')
    if room:
        leave_room(room)
        
        sid = request.sid
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("UPDATE connections SET room = NULL, last_active = ? WHERE sid = ?", (datetime.now(), sid))
        conn.commit()
        conn.close()
        
        emit('left', {'room': room})


@socketio.on('disconnect')
def handle_disconnect():
    """处理断开连接"""
    sid = request.sid
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM connections WHERE sid = ?", (sid,))
    conn.commit()
    conn.close()


@app.route('/api/ws/stats', methods=['GET'])
def get_stats():
    """获取 WebSocket 统计信息"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 连接数
    c.execute("SELECT COUNT(*) FROM connections")
    connections = c.fetchone()[0]
    
    # 消息数（最近24小时）
    c.execute(
        "SELECT COUNT(*) FROM messages WHERE timestamp > datetime('now', '-1 day')"
    )
    messages_24h = c.fetchone()[0]
    
    conn.close()
    
    return {
        'success': True,
        'connections': connections,
        'messages_24h': messages_24h,
        'timestamp': datetime.now().isoformat()
    }


if __name__ == "__main__":
    init_db()
    print("=" * 50)
    print("🔌 WebSocket 实时推送服务")
    print("=" * 50)
    print("端口: 5013")
    print("=" * 50)
    socketio.run(app, host="0.0.0.0", port=5013, debug=False)
