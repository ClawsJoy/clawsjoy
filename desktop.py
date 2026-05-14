import webview
import threading
import subprocess
import time
import os
import signal

backend_process = None

def start_backend():
    global backend_process
    backend_process = subprocess.Popen(
        ['python3', 'agent_gateway_clean.py'],
        cwd=os.path.dirname(__file__),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2)

def stop_backend():
    if backend_process:
        backend_process.terminate()
        backend_process.wait()

if __name__ == '__main__':
    start_backend()
    try:
        webview.create_window(
            'ClawsJoy AI 助手', 
            'http://localhost:5002',
            width=1280,
            height=800,
            resizable=True,
            fullscreen=False,
            min_size=(800, 600)
        )
        webview.start()
    finally:
        stop_backend()
