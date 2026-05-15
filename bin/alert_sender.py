#!/usr/bin/env python3
"""告警发送器 - 支持钉钉/飞书/企微，按需触发"""

import json
import requests
import sys
from pathlib import Path

# ========== 配置区（用户根据需要填写）==========
# 钉钉
DINGTALK_WEBHOOK = ""  # 例如: https://oapi.dingtalk.com/robot/send?access_token=xxx
# 飞书
FEISHU_WEBHOOK = ""    # 例如: https://open.feishu.cn/open-apis/bot/v2/hook/xxx
# 企业微信
WECHAT_WEBHOOK = ""    # 例如: https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
# ==============================================

ALERT_LOG = Path("/mnt/d/clawsjoy/logs/alerts.log")
METRICS_FILE = Path("/mnt/d/clawsjoy/data/metrics.json")

def send_dingtalk(message, title="ClawsJoy 告警"):
    """发送钉钉消息"""
    if not DINGTALK_WEBHOOK:
        return False
    headers = {"Content-Type": "application/json"}
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": f"## {title}\n\n{message}\n\n**时间**: {__import__('time').strftime('%Y-%m-%d %H:%M:%S')}"
        }
    }
    try:
        resp = requests.post(DINGTALK_WEBHOOK, json=data, headers=headers, timeout=5)
        return resp.status_code == 200
    except:
        return False

def send_feishu(message, title="ClawsJoy 告警"):
    """发送飞书消息"""
    if not FEISHU_WEBHOOK:
        return False
    data = {
        "msg_type": "text",
        "content": {"text": f"[{title}]\n{message}"}
    }
    try:
        resp = requests.post(FEISHU_WEBHOOK, json=data, timeout=5)
        return resp.status_code == 200
    except:
        return False

def send_wechat(message, title="ClawsJoy 告警"):
    """发送企业微信消息"""
    if not WECHAT_WEBHOOK:
        return False
    data = {
        "msgtype": "markdown",
        "markdown": {"content": f"## {title}\n{message}"}
    }
    try:
        resp = requests.post(WECHAT_WEBHOOK, json=data, timeout=5)
        return resp.status_code == 200
    except:
        return False

def send_to_all(message, title="ClawsJoy 告警"):
    """发送到所有已配置的平台"""
    results = {
        "dingtalk": send_dingtalk(message, title),
        "feishu": send_feishu(message, title),
        "wechat": send_wechat(message, title)
    }
    return results

def get_latest_alerts(n=5):
    """获取最近 N 条告警"""
    if not ALERT_LOG.exists():
        return []
    with open(ALERT_LOG) as f:
        content = f.read()
    alerts = []
    for line in content.split('\n'):
        if line.strip() and not line.startswith('202'):
            alerts.append(line.strip())
    return alerts[-n:]

def get_system_status():
    """获取当前系统状态摘要"""
    if METRICS_FILE.exists():
        with open(METRICS_FILE) as f:
            metrics = json.load(f)
        services = metrics.get("services", {})
        up = sum(1 for s in services.values() if s.get("status") == "up")
        total = len(services)
        res = metrics.get("resources", {})
        return f"📊 服务: {up}/{total} 正常 | 💾 磁盘: {res.get('disk_usage_percent', '?')}% | 🧠 内存: {res.get('memory_percent', '?')}%"
    return "无法获取系统状态"

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ClawsJoy 告警发送器")
    parser.add_argument("--message", "-m", help="自定义告警消息")
    parser.add_argument("--title", "-t", default="ClawsJoy 告警", help="告警标题")
    parser.add_argument("--platform", "-p", choices=["dingtalk", "feishu", "wechat", "all"], 
                       default="all", help="发送平台")
    parser.add_argument("--status", action="store_true", help="发送系统状态")
    parser.add_argument("--latest", action="store_true", help="发送最近告警")
    
    args = parser.parse_args()
    
    if args.status:
        message = get_system_status()
    elif args.latest:
        alerts = get_latest_alerts()
        if alerts:
            message = "📋 最近告警:\n" + "\n".join(alerts)
        else:
            message = "✅ 无未处理告警"
    elif args.message:
        message = args.message
    else:
        # 默认发送系统状态
        message = get_system_status()
    
    print(f"📢 发送: {message[:50]}...")
    
    if args.platform == "dingtalk":
        result = send_dingtalk(message, args.title)
        print(f"钉钉: {'✅ 成功' if result else '❌ 失败'}")
    elif args.platform == "feishu":
        result = send_feishu(message, args.title)
        print(f"飞书: {'✅ 成功' if result else '❌ 失败'}")
    elif args.platform == "wechat":
        result = send_wechat(message, args.title)
        print(f"企微: {'✅ 成功' if result else '❌ 失败'}")
    else:
        results = send_to_all(message, args.title)
        for platform, success in results.items():
            print(f"{platform}: {'✅ 成功' if success else '❌ 失败'}")
