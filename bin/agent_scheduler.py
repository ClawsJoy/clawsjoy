#!/usr/bin/env python3
import json
import subprocess
import sys
import os
import requests

OLLAMA_URL = "http://172.21.80.1:11434/api/generate"

# 正确的图片目录
IMAGE_DIR = os.path.expanduser("~/.openclaw/web/images/hongkong")

PROMPT_TEMPLATE = f"""你是一个任务执行助手。根据任务，输出要执行的bash命令，只输出命令，不要输出任何解释。

可用命令：
- 采集图片: ~/clawsjoy/bin/spider_unsplash "关键词" 数量
- 提交文章: ~/clawsjoy/bin/write_review "标题" "内容" writer
- 制作视频: ~/clawsjoy/bin/make_video "脚本内容" "{IMAGE_DIR}" "输出.mp4" "标题"

用户任务：%s

输出命令（只输出命令）："""


def call_ollama(prompt):
    resp = requests.post(
        OLLAMA_URL,
        json={"model": "qwen2.5:7b", "prompt": prompt, "stream": False},
        timeout=60,
    )
    return resp.json().get("response", "")


def main(task):
    prompt = PROMPT_TEMPLATE % task
    raw = call_ollama(prompt)
    # 提取命令
    lines = raw.strip().split("\n")
    cmd = None
    for line in lines:
        if "~/clawsjoy" in line:
            cmd = line.strip()
            break
    if not cmd:
        cmd = raw.strip()

    print(f"📋 执行: {cmd}")
    if cmd and "~/clawsjoy" in cmd:
        subprocess.run(cmd, shell=True)
    else:
        print("❌ 未生成有效命令")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: agent_scheduler.py <任务描述>")
        sys.exit(1)
    main(" ".join(sys.argv[1:]))
