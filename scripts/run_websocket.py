#!/usr/bin/env python3
#!/usr/bin/env python3
"""Run Websocket - Run Websocket 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ws_server.server import app, socketio

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5003, debug=False)
