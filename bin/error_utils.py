#!/usr/bin/env python3
"""统一错误响应格式"""

import json
from typing import Dict, Any, Optional

# 标准错误码
ERROR_CODES = {
    # 4xx 客户端错误
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "CONFLICT": 409,
    "VALIDATION_ERROR": 422,
    "TOO_MANY_REQUESTS": 429,
    # 5xx 服务端错误
    "INTERNAL_ERROR": 500,
    "SERVICE_UNAVAILABLE": 503,
    "TIMEOUT": 504,
}


def error_response(code: str, message: str, details: Optional[Dict] = None) -> Dict:
    """生成统一格式的错误响应"""
    http_code = ERROR_CODES.get(code, 500)
    response = {
        "success": False,
        "error": {"code": code, "http_code": http_code, "message": message},
    }
    if details:
        response["error"]["details"] = details
    return response


def success_response(data: Any = None, message: str = "success") -> Dict:
    """生成统一格式的成功响应"""
    response = {"success": True, "message": message}
    if data is not None:
        response["data"] = data
    return response


def send_json_response(handler, data: Dict, status: int = 200):
    """发送 JSON 响应"""
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(json.dumps(data, ensure_ascii=False).encode())


def send_error(handler, code: str, message: str, details: Optional[Dict] = None):
    """发送错误响应"""
    http_code = ERROR_CODES.get(code, 500)
    data = error_response(code, message, details)
    send_json_response(handler, data, http_code)


def send_success(
    handler, data: Any = None, message: str = "success", status: int = 200
):
    """发送成功响应"""
    data = success_response(data, message)
    send_json_response(handler, data, status)


if __name__ == "__main__":
    # 测试
    print(error_response("UNAUTHORIZED", "用户名或密码错误"))
    print(success_response({"id": 1}, "创建成功"))
