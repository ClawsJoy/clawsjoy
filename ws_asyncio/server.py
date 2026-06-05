#!/usr/bin/env python3
"""WebSocket 实时推送服务 - asyncio 版本"""

import asyncio
import json
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import websockets
from aiohttp import web

from lib.auth_api import auth_manager

# 数据库初始化
DB_PATH = Path(__file__).parent.parent / "data/websocket.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

connected_clients = {}  # user_id -> websocket


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS offline_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            event TEXT NOT NULL,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    conn.commit()
    conn.close()


init_db()


def save_offline_message(user_id: str, event: str, data: dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO offline_messages (user_id, event, data) VALUES (?, ?, ?)",
        (user_id, event, json.dumps(data)),
    )
    conn.commit()
    conn.close()


def get_offline_messages(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id, event, data FROM offline_messages WHERE user_id = ? ORDER BY id",
        (user_id,),
    )
    rows = c.fetchall()
    c.execute("DELETE FROM offline_messages WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    messages = []
    for row in rows:
        messages.append({"id": row[0], "event": row[1], "data": json.loads(row[2])})
    return messages


async def send_to_user(user_id: str, event: str, data: dict):
    if user_id in connected_clients:
        try:
            message = json.dumps(
                {"event": event, "data": data, "timestamp": time.time()}
            )
            await connected_clients[user_id].send(message)
            print(f"📤 发送到用户 {user_id}: {event}")
            return True
        except Exception as e:
            if user_id in connected_clients:
                del connected_clients[user_id]
            return False
    else:
        save_offline_message(user_id, event, data)
        print(f"💾 用户 {user_id} 离线，消息已保存")
        return False


async def websocket_handler(websocket):
    user_id = None
    try:
        message = await websocket.recv()
        data = json.loads(message)

        if data.get("event") != "auth":
            await websocket.send(
                json.dumps(
                    {"event": "error", "data": {"error": "First message must be auth"}}
                )
            )
            return

        token = data.get("data", {}).get("token", "")
        payload = auth_manager.verify_token(token)

        if not payload:
            await websocket.send(
                json.dumps({"event": "auth_error", "data": {"error": "Invalid token"}})
            )
            return

        user_id = payload.get("user_id")
        username = payload.get("username", user_id)

        connected_clients[user_id] = websocket

        offline = get_offline_messages(user_id)
        for msg in offline:
            await websocket.send(
                json.dumps(
                    {
                        "event": msg["event"],
                        "data": msg["data"],
                        "timestamp": time.time(),
                    }
                )
            )

        await websocket.send(
            json.dumps(
                {
                    "event": "auth_success",
                    "data": {
                        "user_id": user_id,
                        "username": username,
                        "offline_count": len(offline),
                    },
                }
            )
        )
        print(f"🔐 用户认证成功: {username} ({user_id})")

        async for message in websocket:
            try:
                msg_data = json.loads(message)
                event = msg_data.get("event")
                if event == "ping":
                    await websocket.send(
                        json.dumps(
                            {"event": "pong", "data": {"timestamp": time.time()}}
                        )
                    )
            except Exception as e:
                pass

    except websockets.exceptions.ConnectionClosed:
        print(f"❌ 连接关闭: {user_id}")
    finally:
        if user_id and user_id in connected_clients:
            del connected_clients[user_id]


async def push_api(request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        event = data.get("event")
        msg_data = data.get("data", {})

        if not user_id or not event:
            return web.json_response(
                {"success": False, "error": "user_id and event required"}, status=400
            )

        success = await send_to_user(user_id, event, msg_data)
        return web.json_response({"success": success})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=500)


async def stats_api(request):
    return web.json_response(
        {
            "success": True,
            "active_connections": len(connected_clients),
            "users": list(connected_clients.keys()),
        }
    )


async def index_page(request):
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ClawsJoy WebSocket 测试</title>
    <style>
        body { font-family: monospace; padding: 20px; background: #1a1a2e; color: #eee; }
        #log { background: #0f3460; padding: 15px; border-radius: 8px; height: 400px; overflow-y: auto; }
        .msg { margin: 5px 0; padding: 5px; border-radius: 4px; }
        .in { color: #00ff88; }
        .out { color: #00d4ff; }
        input, button { padding: 8px 12px; margin: 5px; border-radius: 4px; border: none; }
        input { background: #0f3460; color: #eee; width: 400px; }
        button { background: #00d4ff; color: #1a1a2e; cursor: pointer; }
    </style>
</head>
<body>
    <h1>🔌 ClawsJoy WebSocket 测试</h1>
    <div>
        <input type="text" id="token" placeholder="JWT Token" style="width: 500px">
        <button onclick="connect()">连接</button>
        <button onclick="disconnect()">断开</button>
    </div>
    <div id="log"></div>
    <script>
        let ws = null;
        function log(msg, type) {
            const div = document.createElement('div');
            div.className = `msg ${type}`;
            div.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
            document.getElementById('log').appendChild(div);
            document.getElementById('log').scrollTop = document.getElementById('log').scrollHeight;
        }
        function connect() {
            const token = document.getElementById('token').value;
            if (!token) { log('请输入 Token', 'out'); return; }
            ws = new WebSocket('ws://localhost:5003');
            ws.onopen = () => {
                log('WebSocket 连接成功', 'in');
                ws.send(JSON.stringify({event: 'auth', data: {token: token}}));
            };
            ws.onmessage = (e) => {
                const data = JSON.parse(e.data);
                log(`收到: ${data.event}`, 'in');
            };
            ws.onclose = () => log('连接关闭', 'out');
            ws.onerror = () => log('连接错误', 'out');
        }
        function disconnect() { if (ws) ws.close(); }
    </script>
</body>
</html>"""
    return web.Response(text=html, content_type="text/html")


async def main():
    # HTTP 应用
    app = web.Application()
    app.router.add_post("/api/push", push_api)
    app.router.add_get("/api/stats", stats_api)
    app.router.add_get("/", index_page)

    # 启动 HTTP 服务
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 5004)
    await site.start()

    print("=" * 50)
    print("🔌 ClawsJoy WebSocket 服务")
    print("=" * 50)
    print("📡 WebSocket: ws://localhost:5003")
    print("📡 HTTP API: http://localhost:5004/api/push")
    print("📄 测试页面: http://localhost:5004")
    print("=" * 50)

    # 启动 WebSocket 服务
    async with websockets.serve(websocket_handler, "0.0.0.0", 5003):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
