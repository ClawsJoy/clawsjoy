#!/usr/bin/env python3
"""ClawsJoy 租户管理 API。

基于本地文件目录保存租户配置，每个租户对应一个 `tenant_<id>` 目录。
"""

import json
import os
import time
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from settings import TENANTS_DIR, PORT_TENANT
from py_logging import get_logger

TENANTS_DIR.mkdir(parents=True, exist_ok=True)
LOGGER = get_logger("tenant_api")

# 默认租户配置
DEFAULT_CONFIG = {
    "evolution_enabled": True,
    "max_concurrent_tasks": 5,
    "quota": {"monthly_tasks": 1000, "storage_mb": 1024},
}


class TenantHandler(BaseHTTPRequestHandler):
    """处理租户相关 HTTP 请求的简单 API 处理器。"""

    def do_GET(self):
        """处理查询类接口：租户列表、单租户配置、租户统计。"""
        parsed = urlparse(self.path)

        if parsed.path == "/api/tenants":
            # 列出所有租户：从 tenant_<id> 目录推导租户 ID，再读取配置名称。
            tenants = []
            for d in TENANTS_DIR.glob("tenant_*"):
                tenant_id = d.name.split("_")[1]
                config_file = d / "config.json"
                if config_file.exists():
                    config = json.loads(config_file.read_text())
                else:
                    # 历史目录可能缺失配置文件，回退到默认配置保证接口可用。
                    config = DEFAULT_CONFIG.copy()
                    config["tenant_id"] = tenant_id
                tenants.append(
                    {"id": tenant_id, "name": config.get("name", f"租户{tenant_id}")}
                )
            self.send_json({"success": True, "tenants": tenants})

        elif parsed.path.startswith("/api/tenants/"):
            # 获取单个租户配置：路径格式 /api/tenants/<tenant_id>
            parts = parsed.path.split("/")
            tenant_id = parts[3] if len(parts) > 3 else None
            if tenant_id:
                config_file = TENANTS_DIR / f"tenant_{tenant_id}" / "config.json"
                if config_file.exists():
                    config = json.loads(config_file.read_text())
                else:
                    # 未创建配置时返回默认值，便于前端首次初始化。
                    config = DEFAULT_CONFIG.copy()
                    config["tenant_id"] = tenant_id
                self.send_json({"success": True, "config": config})
            else:
                self.send_json({"error": "tenant_id required"}, 400)

        elif parsed.path == "/api/tenants/stats":
            # 统计租户和任务文件数量（以租户目录下 json 文件数作为粗略任务数）。
            stats = {"total": 0, "tenants": []}
            for d in TENANTS_DIR.glob("tenant_*"):
                tenant_id = d.name.split("_")[1]
                tasks = list((TENANTS_DIR / f"tenant_{tenant_id}").glob("*.json"))
                stats["tenants"].append({"id": tenant_id, "tasks": len(tasks)})
                stats["total"] += 1
            self.send_json({"success": True, "stats": stats})

        else:
            self.send_error(404)

    def do_POST(self):
        """处理写入类接口：创建租户、更新租户配置。"""
        if self.path == "/api/tenants":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            # 未显式提供 ID 时使用秒级时间戳生成。
            tenant_id = data.get("id", str(int(time.time())))
            name = data.get("name", f"租户{tenant_id}")

            tenant_dir = TENANTS_DIR / f"tenant_{tenant_id}"
            tenant_dir.mkdir(exist_ok=True)

            config = DEFAULT_CONFIG.copy()
            config["name"] = name
            config["tenant_id"] = tenant_id
            config["created_at"] = __import__("datetime").datetime.now().isoformat()

            config_file = tenant_dir / "config.json"
            config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False))

            self.send_json({"success": True, "tenant": {"id": tenant_id, "name": name}})

        elif self.path == "/api/tenants/config":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            tenant_id = data.get("tenant_id")
            if not tenant_id:
                self.send_json({"error": "tenant_id required"}, 400)
                return

            config_file = TENANTS_DIR / f"tenant_{tenant_id}" / "config.json"
            if not config_file.exists():
                self.send_json({"error": "tenant not found"}, 404)
                return

            # 浅层更新配置字段：仅覆盖传入的顶层键。
            config = json.loads(config_file.read_text())
            for key, value in data.get("config", {}).items():
                config[key] = value
            config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False))

            self.send_json({"success": True, "config": config})

        else:
            self.send_error(404)

    def do_DELETE(self):
        """删除租户目录及其配置/数据。"""
        if self.path.startswith("/api/tenants/"):
            tenant_id = self.path.split("/")[-1]
            tenant_dir = TENANTS_DIR / f"tenant_{tenant_id}"
            if tenant_dir.exists():
                import shutil

                shutil.rmtree(tenant_dir)
                self.send_json(
                    {"success": True, "message": f"Tenant {tenant_id} deleted"}
                )
            else:
                self.send_json({"error": "tenant not found"}, 404)
        else:
            self.send_error(404)

    def send_json(self, data, status=200):
        """统一 JSON 响应格式，并附带基础 CORS 头。"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def do_OPTIONS(self):
        """处理浏览器预检请求。"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        """记录标准访问日志。"""
        LOGGER.info(format % args)


if __name__ == "__main__":
    port = PORT_TENANT
    LOGGER.info("Tenant API started: http://redis:%s", port)
    LOGGER.info("Route: GET /api/tenants - list tenants")
    LOGGER.info("Route: GET /api/tenants/{tenant_id} - get tenant")
    LOGGER.info("Route: POST /api/tenants - create tenant")
    LOGGER.info("Route: POST /api/tenants/config - update config")
    LOGGER.info("Route: DELETE /api/tenants/{tenant_id} - delete tenant")
    HTTPServer(("0.0.0.0", port), TenantHandler).serve_forever()
