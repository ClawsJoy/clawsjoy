#!/usr/bin/env python3
"""Butler API - 管家接口（增强版）"""

from flask import Blueprint, jsonify, request
import json
from pathlib import Path
from datetime import datetime
import time
import re

api_bp = Blueprint("v5_butler", __name__)

DATA_DIR = Path("data/butler")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 内存缓存
_cache = {}
_cache_ttl = 600  # 10分钟缓存


def get_data(user_id):
    """获取用户数据（带缓存）"""
    cache_key = f"butler_data_{user_id}"
    
    if cache_key in _cache:
        data, timestamp = _cache[cache_key]
        if time.time() - timestamp < _cache_ttl:
            return data
    
    file_path = DATA_DIR / f"{user_id}.json"
    if file_path.exists():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {"todos": [], "reminders": [], "preferences": [], "calendar": []}
    else:
        data = {"todos": [], "reminders": [], "preferences": [], "calendar": []}
    
    _cache[cache_key] = (data, time.time())
    return data


def save_data(user_id, data):
    """保存用户数据"""
    file_path = DATA_DIR / f"{user_id}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    cache_key = f"butler_data_{user_id}"
    _cache[cache_key] = (data, time.time())


def parse_time(text):
    """解析时间字符串"""
    match = re.search(r'(\d{1,2})[:点](\d{2})?', text)
    if match:
        hour = match.group(1)
        minute = match.group(2) or "00"
        return f"{hour}:{minute}"
    return None


@api_bp.route("/butler/info", methods=["GET"])
def info():
    user_id = request.args.get("user_id", "default")
    data = get_data(user_id)
    return jsonify({
        "success": True,
        "name": "小管",
        "version": "4.0",
        "user_id": user_id,
        "todos_count": len(data.get("todos", [])),
        "reminders_count": len(data.get("reminders", [])),
        "service": "butler"
    })


@api_bp.route("/butler/chat", methods=["POST"])
def chat():
    data_req = request.get_json() or {}
    user_id = data_req.get("user_id", "default")
    message = data_req.get("message", "")
    user_data = get_data(user_id)
    msg_lower = message.lower()
    
    # 日程安排
    if "安排" in msg_lower and ("明天" in msg_lower or "今天" in msg_lower or "下午" in msg_lower):
        time_str = parse_time(message)
        if time_str:
            task = re.sub(r'安排|明天|今天|在|下午|上午|点|分', '', message).strip()
            if "calendar" not in user_data:
                user_data["calendar"] = []
            user_data["calendar"].append({
                "task": task,
                "time": time_str,
                "date": "明天" if "明天" in msg_lower else "今天",
                "created_at": datetime.now().isoformat()
            })
            save_data(user_id, user_data)
            response = f"✅ 已安排：{task} 在 {time_str}"
        else:
            response = "请说：安排 任务 在 时间"
    
    # 智能建议
    elif "建议" in msg_lower or "推荐" in msg_lower:
        todos = user_data.get("todos", [])
        pending = [t for t in todos if not t.get("completed", False)]
        if pending:
            response = f"💡 建议优先处理：{pending[0].get('task')}"
        else:
            response = "💡 暂无待办，可以休息一下"
    
    # 统计报告
    elif "统计" in msg_lower or "报告" in msg_lower:
        try:
            todos = user_data.get("todos", [])
            completed = 0
            pending = 0
            for t in todos:
                if t.get("completed", False):
                    completed += 1
                else:
                    pending += 1
            response = f"📊 统计报告：\\n   ✅ 已完成: {completed} 项\\n   ⭕ 待完成: {pending} 项\\n   📝 总计: {len(todos)} 项"    
        except Exception as e:
            response = f"统计失败: {e}"
    
    # 清空待办
    elif "清空" in msg_lower and "待办" in msg_lower:
        user_data["todos"] = []
        save_data(user_id, user_data)
        response = "✅ 已清空所有待办"
    
    # 优先级设置
    elif "优先级" in msg_lower:
        parts = re.sub(r'设置优先级|为', '', message).strip().split()
        if len(parts) >= 2:
            task_name = parts[0]
            priority_word = parts[1] if len(parts) > 1 else "中"
            priority_map = {"高": 5, "中": 3, "低": 1}
            priority_val = priority_map.get(priority_word, 3)
            todos = user_data.get("todos", [])
            found = False
            for t in todos:
                if task_name in t.get("task", ""):
                    t["priority"] = priority_val
                    save_data(user_id, user_data)
                    response = f"✅ 已设置 {task_name} 优先级为 {priority_word}"
                    found = True
                    break
            if not found:
                response = f"未找到待办：{task_name}"
        else:
            response = '请说：设置优先级 [任务] 为 高/中/低'
    
    # 添加待办
    elif "添加" in msg_lower and "待办" in msg_lower:
        task = re.sub(r'添加待办|加待办', '', message).strip()
        if not task:
            task = "待办事项"
        user_data["todos"].append({
            "task": task, 
            "completed": False, 
            "created_at": datetime.now().isoformat(),
            "priority": 3
        })
        save_data(user_id, user_data)
        response = f"✅ 已添加待办：{task}"
    
    # 查看待办
    elif "待办" in msg_lower:
        todos = user_data.get("todos", [])
        pending = [t for t in todos if not t.get("completed", False)]
        if pending:
            priority_icons = {5: "🔥", 3: "📌", 1: "📝"}
            response = "📝 待办事项：\n"
            for i, t in enumerate(pending[:10]):
                icon = priority_icons.get(t.get("priority", 3), "📌")
                response += f"{i+1}. {icon} {t.get('task')}\n"
        else:
            response = "暂无待办事项"
    
    # 完成待办
    elif "完成" in msg_lower and "待办" in msg_lower:
        todos = user_data.get("todos", [])
        pending = [t for t in todos if not t.get("completed", False)]
        if pending:
            pending[0]["completed"] = True
            save_data(user_id, user_data)
            response = f"✅ 已完成：{pending[0].get('task')}"
        else:
            response = "暂无待办事项"
    
    # 记住信息
    elif "记住" in msg_lower:
        parts = message.replace("记住", "").strip().split("是")
        if len(parts) == 2:
            key, val = parts[0].strip(), parts[1].strip()
            user_data["preferences"][key] = val
            save_data(user_id, user_data)
            response = f"✅ 已记住：{key} = {val}"
        else:
            response = '请说：记住 [内容] 是 [值]'
    
    # 回忆信息
    elif "回忆" in msg_lower:
        key = message.replace("回忆", "").strip()
        val = user_data.get("preferences", {}).get(key)
        response = f"{key} = {val}" if val else f"不记得 {key}"
    
    else:
        response = "您好！我是您的私人管家。\n\n可以说：\n• 查看待办\n• 添加待办 买菜\n• 安排 开会 在 下午3点\n• 统计报告\n• 建议\n• 记住 生日 是 5月1日"
    
    return jsonify({"success": True, "response": response, "service": "butler"})


@api_bp.route("/butler/todo", methods=["GET", "POST"])
def todo():
    if request.method == "POST":
        data = request.get_json() or {}
        user_id = data.get("user_id", "default")
        task = data.get("task", "")
        priority = data.get("priority", 3)
        user_data = get_data(user_id)
        user_data["todos"].append({
            "task": task,
            "completed": False,
            "created_at": datetime.now().isoformat(),
            "priority": priority
        })
        save_data(user_id, user_data)
        return jsonify({"success": True, "message": f"已添加: {task}", "service": "butler"})
    else:
        user_id = request.args.get("user_id", "default")
        status = request.args.get("status", "all")
        sort_by = request.args.get("sort", "created")
        limit = int(request.args.get("limit", 50))
        
        user_data = get_data(user_id)
        todos = user_data.get("todos", [])
        
        if status == "pending":
            todos = [t for t in todos if not t.get("completed", False)]
        elif status == "completed":
            todos = [t for t in todos if t.get("completed", False)]
        
        if sort_by == "priority":
            todos = sorted(todos, key=lambda x: x.get("priority", 3), reverse=True)
        else:
            todos = sorted(todos, key=lambda x: x.get("created_at", ""), reverse=True)
        
        todos = todos[:limit]
        
        return jsonify({
            "success": True, 
            "todos": todos, 
            "total": len(user_data.get("todos", [])),
            "service": "butler"
        })


@api_bp.route("/butler/todo/batch", methods=["POST"])
def batch_todo():
    data = request.get_json() or {}
    user_id = data.get("user_id", "default")
    tasks = data.get("tasks", [])
    
    user_data = get_data(user_id)
    for task in tasks:
        user_data["todos"].append({
            "task": task,
            "completed": False,
            "created_at": datetime.now().isoformat(),
            "priority": 3
        })
    save_data(user_id, user_data)
    
    return jsonify({"success": True, "message": f"已添加 {len(tasks)} 个待办", "service": "butler"})


@api_bp.route("/butler/todo/clear", methods=["POST"])
def clear_completed():
    data = request.get_json() or {}
    user_id = data.get("user_id", "default")
    
    user_data = get_data(user_id)
    user_data["todos"] = [t for t in user_data.get("todos", []) if not t.get("completed", False)]
    save_data(user_id, user_data)
    
    return jsonify({"success": True, "message": "已清除完成的待办", "service": "butler"})


@api_bp.route("/butler/reminder", methods=["GET", "POST"])
def reminder():
    if request.method == "POST":
        data = request.get_json() or {}
        user_id = data.get("user_id", "default")
        title = data.get("title", "")
        time_str = data.get("time", "")
        user_data = get_data(user_id)
        user_data["reminders"].append({
            "title": title,
            "time": time_str,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "created_at": datetime.now().isoformat()
        })
        save_data(user_id, user_data)
        return jsonify({"success": True, "message": f"已设置: {title}", "service": "butler"})
    else:
        user_id = request.args.get("user_id", "default")
        user_data = get_data(user_id)
        return jsonify({"success": True, "reminders": user_data.get("reminders", []), "service": "butler"})


@api_bp.route("/butler/export", methods=["GET"])
def export_data():
    user_id = request.args.get("user_id", "default")
    user_data = get_data(user_id)
    
    return jsonify({
        "success": True,
        "data": user_data,
        "exported_at": datetime.now().isoformat(),
        "service": "butler"
    })


@api_bp.route("/butler/health", methods=["GET"])
def health():
    stats = {
        "service": "butler",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "cache_size": len(_cache)
    }
    return jsonify(stats)
