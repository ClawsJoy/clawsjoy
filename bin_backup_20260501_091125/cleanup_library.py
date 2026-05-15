#!/usr/bin/env python3
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

BASE = "/home/flybo/clawsjoy/tenants"
DAYS = 30
IMPORTANCE_LEVEL = 4

for tenant_dir in Path(BASE).glob("tenant_*"):
    db_path = tenant_dir / "library.db"
    if not db_path.exists():
        continue
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    cutoff = (datetime.now() - timedelta(days=DAYS)).isoformat()
    c.execute("SELECT id, storage_path FROM files WHERE importance = ? AND created_at < ?", (IMPORTANCE_LEVEL, cutoff))
    rows = c.fetchall()
    for file_id, storage_path in rows:
        if os.path.exists(storage_path):
            os.remove(storage_path)
            print(f"🗑️ 删除: {storage_path}")
        c.execute("DELETE FROM files WHERE id = ?", (file_id,))
        c.execute("DELETE FROM file_tags WHERE file_id = ?", (file_id,))
    conn.commit()
    conn.close()
    print(f"✅ {tenant_dir.name} 清理了 {len(rows)} 个不重要文件")
