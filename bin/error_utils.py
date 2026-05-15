"""错误处理工具模块"""

import json
from http.server import BaseHTTPRequestHandler

def send_json_response(handler, data, status=200):
    """发送 JSON 响应"""
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json')
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.end_headers()
    handler.wfile.write(json.dumps(data, ensure_ascii=False).encode())

def send_error(handler, message, status=400):
    """发送错误响应"""
    send_json_response(handler, {'success': False, 'error': message}, status)

def send_success(handler, data=None, message='success'):
    """发送成功响应"""
    response = {'success': True, 'message': message}
    if data:
        response.update(data)
    send_json_response(handler, response)
