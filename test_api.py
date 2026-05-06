#!/usr/bin/env python3
import requests
import time

LONG_SCRIPT = """香港优才计划2026年迎来重大调整。综合计分制最低分数从80分降至75分。新增金融科技、人工智能、数据科学人才清单。审批时间从6个月缩短至3个月。2025年共有3421人获批，成功率38%。申请需要准备学历证明、工作证明、语言成绩。建议尽早准备材料。"""

print(f"脚本长度: {len(LONG_SCRIPT)}")

for i in range(3):
    try:
        resp = requests.post("http://localhost:8105/api/promo/make",
            json={"topic": "香港优才计划", "script": LONG_SCRIPT},
            timeout=180)
        print(resp.json())
        break
    except Exception as e:
        print(f"尝试 {i+1}/3 失败: {e}")
        if i < 2:
            time.sleep(5)
