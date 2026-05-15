#!/usr/bin/env python3
import sys
import subprocess

task = sys.argv[1] if len(sys.argv) > 1 else ""

if "视频" in task or "制作" in task:
    print("📋 执行: 制作视频")
    subprocess.run(["curl", "-s", "-X", "POST", "http://localhost:8105/api/promo/make",
                    "-H", "Content-Type: application/json",
                    "-d", '{"city":"香港","style":"人文"}'])
else:
    print(f"未知任务: {task}")
