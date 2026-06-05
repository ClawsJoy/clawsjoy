#!/usr/bin/env python3
"""Manual Integrate - Manual Integrate 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

import os
import re

gateway_file = "agent_gateway_web.py"

# 读取文件
with open(gateway_file, "r") as f:
    content = f.read()

# 检查是否已有通信初始化
if "init_agent_communication" in content:
    print("✅ 通信初始化代码已存在")
    # 显示相关行
    for i, line in enumerate(content.split("\n")):
        if "init_agent_communication" in line:
            print(f"  第{i+1}行: {line[:80]}")
    exit(0)

# 找到 app.run() 或 if __name__ 的位置
lines = content.split("\n")
insert_pos = -1
insert_line = None

for i, line in enumerate(lines):
    if "app.run(" in line or "app.run(" in line:
        insert_pos = i
        insert_line = "    # 初始化 Agent 通信系统"
        print(f"找到 app.run() 在第 {i+1} 行")
        break
    elif 'if __name__ == "__main__":' in line:
        insert_pos = i + 1
        insert_line = "    # 初始化 Agent 通信系统"
        print(f"找到 if __name__ 在第 {i+1} 行")

if insert_pos > 0:
    # 构建要插入的代码块
    init_block = """
    # ========== Agent 通信系统初始化 ==========
    try:
        from lib.agent_communication_init import init_agent_communication
        init_agent_communication()
        print("✅ Agent 通信系统已启动")
    except Exception as e:
        print(f"⚠️ Agent 通信系统启动失败: {e}")
    # ==========================================
"""

    # 插入代码
    new_lines = lines[:insert_pos] + [init_block] + lines[insert_pos:]

    # 备份原文件
    os.system(f"cp {gateway_file} {gateway_file}.bak2")

    # 写入新文件
    with open(gateway_file, "w") as f:
        f.write("\n".join(new_lines))

    print(f"✅ 已添加通信初始化代码到第 {insert_pos+1} 行之前")
    print("请重启网关: pkill -f agent_gateway_web.py && python3 agent_gateway_web.py")
else:
    print("❌ 未找到合适的插入位置")
    print("请手动在 app.run() 之前添加:")
    print(init_block)
