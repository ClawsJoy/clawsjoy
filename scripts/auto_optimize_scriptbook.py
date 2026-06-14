#!/usr/bin/env python3
"""话本自动优化脚本 - 可定时执行"""

import sys
sys.path.insert(0, '/home/flybo/clawsjoy_v5')

import requests
import time

def optimize_all():
    """优化所有 Agent 的话本"""
    agents = ["chat_agent", "butler_agent"]
    
    for agent in agents:
        try:
            resp = requests.post(
                "http://localhost:5002/api/v5/scriptbook/optimize",
                json={"agent": agent, "auto_apply": True},
                timeout=30
            )
            if resp.status_code == 200:
                print(f"✅ {agent} 话本优化完成")
            else:
                print(f"❌ {agent} 话本优化失败: {resp.text}")
        except Exception as e:
            print(f"❌ {agent} 优化失败: {e}")

if __name__ == "__main__":
    optimize_all()
