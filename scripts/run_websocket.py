#!/usr/bin/env python3
"""WebSocket 服务启动脚本"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ws_server.server import socketio, app

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5003, debug=False)
