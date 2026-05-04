#!/usr/bin/env python3
"""ClawsJoy 统一错误处理模块"""

import json
import traceback
from functools import wraps
from http.server import BaseHTTPRequestHandler

# 错误码定义
ERROR_CODES = {
    # 4xx 客户端错误
    400: {"code": "BAD_REQUEST", "message": "请求参数错误"},
    401: {"code": "UNAUTHORIZED", "message": "未授权，请登录"},
    403: {"code": "FORBIDDEN", "message": "禁止访问"},
    404: {"code": "NOT_FOUND", "message": "资源不存在"},
    429: {"code": "TOO_MANY_REQUESTS", "message": "请求过于频繁"},
    
    # 5xx 服务端错误
    500: {"code": "INTERNAL_ERROR", "message": "服务器内部错误"},
    502: {"code": "BAD_GATEWAY", "message": "网关错误"},
    503: {"code": "SERVICE_UNAVAILABLE", "message": "服务不可用"},
    504: {"code": "GATEWAY_TIMEOUT", "message": "网关超时"},
}

def success_response(data=None, message="success"):
    """成功响应"""
    return {
        "success": True,
        "code": 200,
        "message": message,
        "data": data,
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }

def error_response(code=500, error_detail=None, custom_message=None):
    """错误响应"""
    err_info = ERROR_CODES.get(code, ERROR_CODES[500])
    return {
        "success": False,
        "code": code,
        "error": {
            "code": err_info["code"],
            "message": custom_message or err_info["message"],
            "detail": error_detail
        },
        "timestamp": __import__('datetime').datetime.now().isoformat()
    }

def safe_execute(func):
    """装饰器：安全执行，捕获异常"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            error_detail = traceback.format_exc() if __debug__ else str(e)
            self.send_error_response(500, error_detail)
    return wrapper

class ErrorHandlerMixin:
    """错误处理混入类"""
    
    def send_success(self, data=None, message="success"):
        """发送成功响应"""
        self.send_json(success_response(data, message))
    
    def send_error_response(self, code=500, detail=None, message=None):
        """发送错误响应"""
        self.send_json(error_response(code, detail, message), code)
    
    def send_json(self, data, status=200):
        """发送 JSON 响应"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def validate_required_params(self, data, required_params):
        """验证必填参数"""
        missing = [p for p in required_params if not data.get(p)]
        if missing:
            self.send_error_response(400, f"缺少必填参数: {', '.join(missing)}")
            return False
        return True

if __name__ == "__main__":
    # 测试
    print(success_response({"test": "ok"}))
    print(error_response(404))
