#!/usr/bin/env python3
"""ClawsJoy 计费系统 API。

提供余额查询、用量统计、使用计费记录、充值与套餐查询能力。
"""

import sqlite3
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from settings import DATA_DIR, PORT_BILLING
from py_logging import get_logger

# 数据库路径
DB_PATH = DATA_DIR / "billing.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
LOGGER = get_logger("billing_api")

# 计费标准（可按需配置）
PRICES = {
    "chat": 0.001,  # 对话 0.1 分/次
    "code_generation": 0.005,  # 代码生成 0.5 分/次
    "promo": 0.01,  # 宣传片 1 分/次
    "spider": 0.002,  # 图片采集 0.2 分/次
    "storage_mb": 0.0001,  # 存储 0.01 分/MB/天
}


def init_db():
    """初始化计费数据库与默认套餐。"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 计费记录表
    c.execute("""
        CREATE TABLE IF NOT EXISTS billing_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id TEXT NOT NULL,
            task_type TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            price REAL NOT NULL,
            total REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'
        )
    """)

    # 租户余额表
    c.execute("""
        CREATE TABLE IF NOT EXISTS tenant_balance (
            tenant_id TEXT PRIMARY KEY,
            balance REAL DEFAULT 0.0,
            credit_limit REAL DEFAULT 100.0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 套餐表
    c.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quota_chat INTEGER,
            quota_code INTEGER,
            quota_promo INTEGER,
            description TEXT
        )
    """)

    # 插入默认套餐
    c.execute("SELECT COUNT(*) FROM plans")
    if c.fetchone()[0] == 0:
        default_plans = [
            ("免费版", 0, 100, 10, 1, "基础功能，限量使用"),
            ("专业版", 49, 1000, 200, 20, "更多配额，优先支持"),
            ("企业版", 199, 10000, 2000, 200, "无限配额，专属支持"),
        ]
        c.executemany(
            "INSERT INTO plans (name, price, quota_chat, quota_code, quota_promo, description) VALUES (?,?,?,?,?,?)",
            default_plans,
        )

    conn.commit()
    conn.close()
    LOGGER.info("计费数据库初始化完成")


def record_usage(tenant_id: str, task_type: str, quantity: int = 1):
    """记录一次任务用量，并同步扣减租户余额。"""
    price = PRICES.get(task_type, 0.001)
    total = price * quantity

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO billing_records (tenant_id, task_type, quantity, price, total) VALUES (?,?,?,?,?)",
        (tenant_id, task_type, quantity, price, total),
    )

    # 更新余额：余额不存在时为租户初始化一条负余额记录。
    c.execute(
        "UPDATE tenant_balance SET balance = balance - ?, updated_at = CURRENT_TIMESTAMP WHERE tenant_id = ?",
        (total, tenant_id),
    )
    if c.rowcount == 0:
        c.execute(
            "INSERT INTO tenant_balance (tenant_id, balance) VALUES (?, ?)",
            (tenant_id, -total),
        )

    conn.commit()
    conn.close()
    return {"success": True, "cost": total, "balance": get_balance(tenant_id)}


def get_balance(tenant_id: str) -> float:
    """获取租户当前余额。"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT balance FROM tenant_balance WHERE tenant_id = ?", (tenant_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0.0


def get_usage(tenant_id: str, days: int = 30):
    """获取租户在指定天数内的任务使用统计。"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    c.execute(
        """
        SELECT task_type, SUM(quantity) as total_count, SUM(total) as total_cost
        FROM billing_records
        WHERE tenant_id = ? AND created_at > ?
        GROUP BY task_type
    """,
        (tenant_id, cutoff),
    )
    rows = c.fetchall()
    conn.close()
    return [{"task_type": r[0], "count": r[1], "cost": r[2]} for r in rows]


def get_all_tenants_usage(days: int = 30):
    """获取所有租户使用统计（管理员视角）。"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    c.execute(
        """
        SELECT tenant_id, task_type, SUM(quantity) as total_count, SUM(total) as total_cost
        FROM billing_records
        WHERE created_at > ?
        GROUP BY tenant_id, task_type
        ORDER BY total_cost DESC
    """,
        (cutoff,),
    )
    rows = c.fetchall()
    conn.close()

    result = {}
    for r in rows:
        if r[0] not in result:
            result[r[0]] = {"total_cost": 0, "details": []}
        result[r[0]]["total_cost"] += r[3]
        result[r[0]]["details"].append({"task_type": r[1], "count": r[2], "cost": r[3]})
    return result


class BillingHandler(BaseHTTPRequestHandler):
    """计费相关 HTTP 处理器。"""

    def do_GET(self):
        """处理余额、统计、套餐等查询接口。"""
        parsed = urlparse(self.path)

        if parsed.path == "/api/billing/balance":
            params = parse_qs(parsed.query)
            tenant_id = params.get("tenant_id", ["1"])[0]
            self.send_json({"tenant_id": tenant_id, "balance": get_balance(tenant_id)})

        elif parsed.path == "/api/billing/usage":
            params = parse_qs(parsed.query)
            tenant_id = params.get("tenant_id", ["1"])[0]
            days = int(params.get("days", ["30"])[0])
            self.send_json(
                {"tenant_id": tenant_id, "usage": get_usage(tenant_id, days)}
            )

        elif parsed.path == "/api/billing/admin/tenants":
            days = int(parsed.query.split("=")[1]) if "=" in parsed.query else 30
            self.send_json({"tenants": get_all_tenants_usage(days)})

        elif parsed.path == "/api/billing/plans":
            self.send_json({"plans": get_plans()})

        else:
            self.send_error(404)

    def do_POST(self):
        """处理计费记录与充值接口。"""
        if self.path == "/api/billing/record":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            result = record_usage(
                tenant_id=data.get("tenant_id", "1"),
                task_type=data.get("task_type", "chat"),
                quantity=data.get("quantity", 1),
            )
            self.send_json(result)

        elif self.path == "/api/billing/recharge":
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            tenant_id = data.get("tenant_id", "1")
            amount = data.get("amount", 0)

            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(
                "UPDATE tenant_balance SET balance = balance + ? WHERE tenant_id = ?",
                (amount, tenant_id),
            )
            if c.rowcount == 0:
                c.execute(
                    "INSERT INTO tenant_balance (tenant_id, balance) VALUES (?, ?)",
                    (tenant_id, amount),
                )
            conn.commit()
            conn.close()
            self.send_json(
                {
                    "success": True,
                    "tenant_id": tenant_id,
                    "new_balance": get_balance(tenant_id),
                }
            )

        else:
            self.send_error(404)

    def send_json(self, data, status=200):
        """统一 JSON 响应并补充 CORS 头。"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def do_OPTIONS(self):
        """处理浏览器 CORS 预检请求。"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        """记录标准访问日志。"""
        LOGGER.info(format % args)


def get_plans():
    """查询可用套餐列表。"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id, name, price, quota_chat, quota_code, quota_promo, description FROM plans"
    )
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": r[0],
            "name": r[1],
            "price": r[2],
            "quota": {"chat": r[3], "code": r[4], "promo": r[5]},
            "description": r[6],
        }
        for r in rows
    ]


if __name__ == "__main__":
    init_db()
    port = PORT_BILLING
    LOGGER.info("Billing API started: http://redis:%s", port)
    LOGGER.info("Route: GET /api/billing/balance?tenant_id=1")
    LOGGER.info("Route: GET /api/billing/usage?tenant_id=1")
    LOGGER.info("Route: POST /api/billing/record")
    LOGGER.info("Route: POST /api/billing/recharge")
    HTTPServer(("0.0.0.0", port), BillingHandler).serve_forever()
