#!/usr/bin/env python3
"""SQLite 到 PostgreSQL 数据迁移脚本"""

import sqlite3
import psycopg2
from pathlib import Path

# 数据库映射
DB_MAP = {
    "data/auth.db": "clawsjoy_auth",
    "data/billing.db": "clawsjoy_billing",
    "data/conversation.db": "clawsjoy_conversation",
    "data/feedback.db": "clawsjoy_feedback",
    "data/library.db": "clawsjoy_library",
    "data/openclaw_memory.db": "clawsjoy_memory",
    "data/self_learning.db": "clawsjoy_learning",
    "data/tasks.db": "clawsjoy_tasks",
    "data/websocket.db": "clawsjoy_websocket",
}

PG_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "clawsjoy",
    "password": "clawsjoy_local",
}

def get_pg_connection(dbname):
    return psycopg2.connect(
        host=PG_CONFIG["host"],
        port=PG_CONFIG["port"],
        user=PG_CONFIG["user"],
        password=PG_CONFIG["password"],
        database=dbname
    )

def migrate_table(sqlite_conn, pg_conn, table_name):
    """迁移单个表"""
    # 获取表结构
    cursor = sqlite_conn.cursor()
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    result = cursor.fetchone()
    if not result:
        return
    
    # 创建表
    pg_cursor = pg_conn.cursor()
    create_sql = result[0].replace("AUTOINCREMENT", "SERIAL")
    try:
        pg_cursor.execute(create_sql)
    except Exception as e:
        print(f"  创建表 {table_name} 跳过: {e}")
    
    # 迁移数据
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    if not rows:
        return
    
    # 获取列名
    columns = [desc[0] for desc in cursor.description]
    placeholders = ','.join(['%s'] * len(columns))
    insert_sql = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
    
    for row in rows:
        try:
            pg_cursor.execute(insert_sql, row)
        except Exception as e:
            print(f"  插入失败: {e}")
    
    pg_conn.commit()
    print(f"  迁移表 {table_name}: {len(rows)} 行")

def main():
    print("开始迁移 SQLite 到 PostgreSQL...")
    
    for sqlite_path, pg_dbname in DB_MAP.items():
        if not Path(sqlite_path).exists():
            print(f"跳过 {sqlite_path} (文件不存在)")
            continue
        
        print(f"\n迁移 {sqlite_path} -> {pg_dbname}")
        sqlite_conn = sqlite3.connect(sqlite_path)
        pg_conn = get_pg_connection(pg_dbname)
        
        # 获取所有表
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            migrate_table(sqlite_conn, pg_conn, table[0])
        
        sqlite_conn.close()
        pg_conn.close()
    
    print("\n✅ 迁移完成！")

if __name__ == "__main__":
    main()
