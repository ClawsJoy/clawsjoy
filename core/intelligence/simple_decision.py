#!/usr/bin/env python3
"""简化决策引擎 - 每小时记录一次"""
import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
import time
from lib.memory_simple import memory
from datetime import datetime

while True:
    try:
        memory.remember(
            f"决策|{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}|系统运行正常",
            category='executed_decisions'
        )
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 决策已记录")
    except Exception as e:
        print(f"决策记录失败: {e}")
    time.sleep(3600)
