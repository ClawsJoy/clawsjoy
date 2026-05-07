#!/bin/bash
# Agent 自动执行学到的运维技能

# 1. 检查并修复所有服务
python3 -c "
import subprocess
import json
from pathlib import Path

# 检查哪些服务应该运行
services = ['chat-api', 'promo-api', 'agent-api', 'health-api']

for service in services:
    result = subprocess.run(f'pm2 list | grep {service} | grep -q online', shell=True)
    if result.returncode != 0:
        print(f'🔧 Agent 发现 {service} 服务异常，正在修复...')
        subprocess.run(f'cd /mnt/d/clawsjoy/bin && pm2 start {service}.py --interpreter python3 --name {service}', shell=True)
        print(f'✅ {service} 已恢复')
"

# 2. 检查端口冲突
python3 -c "
import subprocess
import re

ports = [18109, 8108, 18103, 18083]
for port in ports:
    result = subprocess.run(f'ss -tlnp | grep :{port}', shell=True, capture_output=True)
    if result.returncode != 0:
        print(f'🔧 Agent 发现端口 {port} 空闲，服务可能未启动')
"

echo "✅ Agent 运维完成"
