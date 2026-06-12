#!/usr/bin/env python3
"""Butler API - 管家接口（标准化 JSON v1.0 完整适配版）"""

from flask import Blueprint, jsonify, request
import json
from pathlib import Path
from datetime import datetime
import time
import re
import uuid

from core.lib.unified_intent_parser import unified_parser

api_bp = Blueprint("v5_butler", __name__)

DATA_DIR = Path("data/butler")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 内存缓存
_cache = {}
_cache_ttl = 600

# 会话存储（临时，生产环境用 Redis）
_session_store = {}


def get_data(user_id):
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
    file_path = DATA_DIR / f"{user_id}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    cache_key = f"butler_data_{user_id}"
    _cache[cache_key] = (data, time.time())


def parse_time(text):
    match = re.search(r'(\d{1,2})[:点](\d{2})?', text)
    if match:
        hour = match.group(1)
        minute = match.group(2) or "00"
        return f"{hour}:{minute}"
    return None


def extract_keywords(text: str) -> list:
    """简单关键词提取"""
    # 移除停用词
    stopwords = {'的', '了', '在', '是', '我', '你', '他', '她', '它', '们'}
    words = re.findall(r'[\u4e00-\u9fa5a-zA-Z0-9]+', text)
    keywords = [w for w in words if w not in stopwords and len(w) > 1]
    return keywords[:5]  # 最多5个


def generate_session_id() -> str:
    return uuid.uuid4().hex[:8]


def generate_thread_id() -> str:
    return uuid.uuid4().hex[:8]


def build_standard_response(
    raw_input: str,
    user_id: str,
    action: str,
    target: str,
    keywords: list,
    output_content: str,
    output_data: dict = None,
    status: str = "completed",
    next_action: str = "done",
    confidence: float = 0.95,
    session_id: str = None,
    thread_id: str = None,
    turn: int = 0
) -> dict:
    """构建标准化 JSON v1.0 响应"""
    if output_data is None:
        output_data = {}
    
    return {
        "version": "1.0",
        "session_id": session_id or generate_session_id(),
        "user_id": user_id,
        "thread_id": thread_id or generate_thread_id(),
        "turn": turn + 1,
        "raw_input": raw_input,
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "target": target,
        "keywords": keywords,
        "confidence": confidence,
        "output_type": "text",
        "output_content": output_content,
        "output_data": output_data,
        "status": status,
        "next": next_action
    }

@api_bp.route("/butler/info", methods=["GET"])
def info():
    user_id = request.args.get("user_id", "default")
    data = get_data(user_id)
    return jsonify({
        "version": "1.0",
        "success": True,
        "name": "小管",
        "version": "4.0",
        "user_id": user_id,
        "todos_count": len(data.get("todos", [])),
        "reminders_count": len(data.get("reminders", [])),
        "service": "butler",
        "timestamp": datetime.now().isoformat()
    })


@api_bp.route("/butler/chat", methods=["POST"])
def chat():
    data_req = request.get_json() or {}
    user_id = data_req.get("user_id", "default")
    message = data_req.get("message", "")
    
    # 获取会话上下文
    session_id = data_req.get("session_id", generate_session_id())
    thread_id = data_req.get("thread_id", generate_thread_id())
    turn = data_req.get("turn", 0)

    # 支持标准化 JSON 输入（来自意图解析器）
    if "action" in data_req:
        return _handle_standard_json(data_req, user_id)

    user_data = get_data(user_id)
    msg_lower = message.lower()

    # ========== 所有功能返回标准化 JSON ==========
    
    # 1. 日历/任务安排
    if "安排" in msg_lower and ("明天" in msg_lower or "今天" in msg_lower or "下午" in msg_lower or "上午" in msg_lower):
        time_str = parse_time(message)
        if time_str:
            task = re.sub(r'安排|明天|今天|在|下午|上午|点|分', '', message).strip()
            if not task:
                task = "未命名任务"
            if "calendar" not in user_data:
                user_data["calendar"] = []
            user_data["calendar"].append({
                "task": task,
                "time": time_str,
                "date": "明天" if "明天" in msg_lower else "今天",
                "created_at": datetime.now().isoformat()
            })
            save_data(user_id, user_data)
            return jsonify(build_standard_response(
                raw_input=message,
                user_id=user_id,
                action="schedule",
                target="task",
                keywords=extract_keywords(task),
                output_content=f"✅ 已安排：{task} 于 {time_str}",
                output_data={"task": task, "time": time_str, "date": "明天" if "明天" in msg_lower else "今天"},
                session_id=session_id,
                thread_id=thread_id,
                turn=turn
            ))
        else:
            return jsonify(build_standard_response(
                raw_input=message,
                user_id=user_id,
                action="schedule",
                target="task",
                keywords=extract_keywords(message),
                output_content="请说：安排 任务 在 时间（如：下午3点）",
                status="failed",
                confidence=0.5,
                session_id=session_id,
                thread_id=thread_id,
                turn=turn
            ))

    # 2. 建议/推荐
    elif "建议" in msg_lower or "推荐" in msg_lower:
        todos = user_data.get("todos", [])
        pending = [t for t in todos if not t.get("completed", False)]
        if pending:
            task = pending[0].get("task")
            return jsonify(build_standard_response(
                raw_input=message,
                user_id=user_id,
                action="recommend",
                target="task",
                keywords=[task],
                output_content=f"💡 建议优先处理：{task}",
                output_data={"suggested_task": task, "pending_count": len(pending)},
                session_id=session_id,
                thread_id=thread_id,
                turn=turn
            ))
        else:
            return jsonify(build_standard_response(
                raw_input=message,
                user_id=user_id,
                action="recommend",
                target="text",
                keywords=[],
                output_content="💡 暂无待办，可以休息一下",
                session_id=session_id,
                thread_id=thread_id,
                turn=turn
            ))

    # 3. 统计报告
    elif "统计" in msg_lower or "报告" in msg_lower:
        todos = user_data.get("todos", [])
        completed = sum(1 for t in todos if t.get("completed", False))
        pending = sum(1 for t in todos if not t.get("completed", False))
        return jsonify(build_standard_response(
            raw_input=message,
            user_id=user_id,
            action="statistics",
            target="task",
            keywords=["统计", "待办"],
            output_content=f"📊 统计报告：\n   ✅ 已完成: {completed} 项\n   ⭕ 待完成: {pending} 项\n   📝 总计: {len(todos)} 项",
            output_data={"completed": completed, "pending": pending, "total": len(todos)},
            session_id=session_id,
            thread_id=thread_id,
            turn=turn
        ))

    # 4. 清空待办
    elif "清空" in msg_lower and "待办" in msg_lower:
        old_count = len(user_data.get("todos", []))
        user_data["todos"] = []
        save_data(user_id, user_data)
        return jsonify(build_standard_response(
            raw_input=message,
            user_id=user_id,
            action="clear",
            target="task",
            keywords=["清空", "待办"],
            output_content=f"✅ 已清空所有待办（共 {old_count} 项）",
            output_data={"cleared_count": old_count},
            session_id=session_id,
            thread_id=thread_id,
            turn=turn
        ))

    # 5. 设置优先级
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
                    return jsonify(build_standard_response(
                        raw_input=message,
                        user_id=user_id,
                        action="update",
                        target="task",
                        keywords=[task_name, priority_word],
                        output_content=f"✅ 已设置 {task_name} 优先级为 {priority_word}",
                        output_data={"task": task_name, "priority": priority_val, "priority_label": priority_word},
                        session_id=session_id,
                        thread_id=thread_id,
                        turn=turn
                    ))
            if not found:
                return jsonify(build_standard_response(
                    raw_input=message,
                    user_id=user_id,
                    action="update",
                    target="task",
                    keywords=[task_name],
                    output_content=f"未找到待办：{task_name}",
                    status="failed",
                    confidence=0.5,
                    session_id=session_id,
                    thread_id=thread_id,
                    turn=turn
                ))
        else:
            return jsonify(build_standard_response(
                raw_input=message,
                user_id=user_id,
                action="update",
                target="task",
                keywords=extract_keywords(message),
                output_content='请说：设置优先级 [任务] 为 高/中/低',
                session_id=session_id,
                thread_id=thread_id,
                turn=turn
            ))

    # 6. 添加待办
    elif "添加" in msg_lower and "待办" in msg_lower:
        task = re.sub(r'添加待办|加待办|添加|加', '', message).strip()
        if not task:
            task = "待办事项"
        user_data["todos"].append({
            "task": task,
            "completed": False,
            "created_at": datetime.now().isoformat(),
            "priority": 3
        })
        save_data(user_id, user_data)
        return jsonify(build_standard_response(
            raw_input=message,
            user_id=user_id,
            action="add",
            target="task",
            keywords=extract_keywords(task),
            output_content=f"✅ 已添加待办：{task}",
            output_data={"task": task, "priority": 3},
            session_id=session_id,
            thread_id=thread_id,
            turn=turn
        ))

    # 7. 查看待办
    elif "待办" in msg_lower and "完成" not in msg_lower:
        todos = user_data.get("todos", [])
        pending = [t for t in todos if not t.get("completed", False)]
        if pending:
            priority_icons = {5: "🔥", 3: "📌", 1: "📝"}
            response_lines = ["📝 待办事项："]
            todo_list = []
            for i, t in enumerate(pending[:10]):
                icon = priority_icons.get(t.get("priority", 3), "📌")
                response_lines.append(f"{i+1}. {icon} {t.get('task')}")
                todo_list.append({"id": i, "task": t.get("task"), "priority": t.get("priority", 3)})
            response = "\n".join(response_lines)
            return jsonify(build_standard_response(
                raw_input=message,
                user_id=user_id,
                action="search",
                target="task",
                keywords=["待办"],
                output_content=response,
                output_data={"todos": todo_list, "pending_count": len(pending), "total_count": len(todos)},
                session_id=session_id,
                thread_id=thread_id,
                turn=turn
            ))
        else:
            return jsonify(build_standard_response(
                raw_input=message,
                user_id=user_id,
                action="search",
                target="task",
                keywords=["待办"],
                output_content="暂无待办事项",
                output_data={"pending_count": 0, "total_count": len(todos)},
                session_id=session_id,
                thread_id=thread_id,
                turn=turn
            ))

    # 8. 完成待办
    elif "完成" in msg_lower and "待办" in msg_lower:
        todos = user_data.get("todos", [])
        pending = [t for t in todos if not t.get("completed", False)]
        if pending:
            completed_task = pending[0].get("task")
            pending[0]["completed"] = True
            save_data(user_id, user_data)
            return jsonify(build_standard_response(
                raw_input=message,
                user_id=user_id,
                action="complete",
                target="task",
                keywords=[completed_task],
                output_content=f"✅ 已完成：{completed_task}",
                output_data={"completed_task": completed_task, "remaining_pending": len(pending) - 1},
                session_id=session_id,
                thread_id=thread_id,
                turn=turn
            ))
        else:
            return jsonify(build_standard_response(
                raw_input=message,
                user_id=user_id,
                action="complete",
                target="task",
                keywords=[],
                output_content="暂无待办事项",
                session_id=session_id,
                thread_id=thread_id,
                turn=turn
            ))

    # 9. 记住偏好
    elif "记住" in msg_lower:
        parts = message.replace("记住", "").strip().split("是")
        if len(parts) == 2:
            key, val = parts[0].strip(), parts[1].strip()
            if "preferences" not in user_data:
                user_data["preferences"] = {}
            user_data["preferences"][key] = val
            save_data(user_id, user_data)
            return jsonify(build_standard_response(
                raw_input=message,
                user_id=user_id,
                action="remember",
                target="info",
                keywords=[key],
                output_content=f"✅ 已记住：{key} = {val}",
                output_data={"key": key, "value": val},
                session_id=session_id,
                thread_id=thread_id,
                turn=turn
            ))
        else:
            return jsonify(build_standard_response(
                raw_input=message,
                user_id=user_id,
                action="remember",
                target="info",
                keywords=extract_keywords(message),
                output_content='请说：记住 [内容] 是 [值]',
                session_id=session_id,
                thread_id=thread_id,
                turn=turn
            ))

    # 10. 回忆偏好
    elif "回忆" in msg_lower:
        key = message.replace("回忆", "").strip()
        val = user_data.get("preferences", {}).get(key)
        if val:
            return jsonify(build_standard_response(
                raw_input=message,
                user_id=user_id,
                action="recall",
                target="info",
                keywords=[key],
                output_content=f"{key} = {val}",
                output_data={"key": key, "value": val},
                session_id=session_id,
                thread_id=thread_id,
                turn=turn
            ))
        else:
            return jsonify(build_standard_response(
                raw_input=message,
                user_id=user_id,
                action="recall",
                target="info",
                keywords=[key],
                output_content=f"不记得 {key}",
                status="failed",
                confidence=0.3,
                session_id=session_id,
                thread_id=thread_id,
                turn=turn
            ))

    # 11. 默认（闲聊/帮助）
    else:
        help_text = """您好！我是您的私人管家。\n\n可以说：\n• 查看待办\n• 添加待办 买菜\n• 安排 开会 在 下午3点\n• 统计报告\n• 建议\n• 记住 生日 是 5月1日"""
        return jsonify(build_standard_response(
            raw_input=message,
            user_id=user_id,
            action="chat",
            target="text",
            keywords=extract_keywords(message),
            output_content=help_text,
            output_data={"help": True},
            session_id=session_id,
            thread_id=thread_id,
            turn=turn
        ))


def _handle_standard_json(standard_json: dict, user_id: str):
    """处理标准化 JSON 输入（来自意图解析器）"""
    action = standard_json.get("action", "chat")
    target = standard_json.get("target", "text")
    keywords = standard_json.get("keywords", [])
    raw_input = standard_json.get("raw_input", "")
    session_id = standard_json.get("session_id", generate_session_id())
    thread_id = standard_json.get("thread_id", generate_thread_id())
    turn = standard_json.get("turn", 0)

    user_data = get_data(user_id)

    # 根据 action + target 分发
    if action == "schedule" and target == "task":
        if keywords:
            task = " ".join(keywords[:3])
            user_data["todos"].append({
                "task": task,
                "completed": False,
                "created_at": datetime.now().isoformat(),
                "priority": 3
            })
            save_data(user_id, user_data)
            return jsonify(build_standard_response(
                raw_input=raw_input,
                user_id=user_id,
                action=action,
                target=target,
                keywords=keywords,
                output_content=f"✅ 已添加待办：{task}",
                output_data={"task": task},
                session_id=session_id,
                thread_id=thread_id,
                turn=turn
            ))

    elif action == "search" and "待办" in " ".join(keywords):
        todos = user_data.get("todos", [])
        pending = [t for t in todos if not t.get("completed", False)]
        if pending:
            response_lines = ["📝 待办事项："]
            todo_list = []
            for i, t in enumerate(pending[:10]):
                response_lines.append(f"{i+1}. {t.get('task')}")
                todo_list.append({"id": i, "task": t.get("task")})
            response = "\n".join(response_lines)
            return jsonify(build_standard_response(
                raw_input=raw_input,
                user_id=user_id,
                action=action,
                target=target,
                keywords=keywords,
                output_content=response,
                output_data={"todos": todo_list, "count": len(pending)},
                session_id=session_id,
                thread_id=thread_id,
                turn=turn
            ))
        else:
            return jsonify(build_standard_response(
                raw_input=raw_input,
                user_id=user_id,
                action=action,
                target=target,
                keywords=keywords,
                output_content="暂无待办事项",
                output_data={"count": 0},
                session_id=session_id,
                thread_id=thread_id,
                turn=turn
            ))

    elif action == "add" and target == "task":
        if keywords:
            task = " ".join(keywords[:3])
            user_data["todos"].append({
                "task": task,
                "completed": False,
                "created_at": datetime.now().isoformat(),
                "priority": 3
            })
            save_data(user_id, user_data)
            return jsonify(build_standard_response(
                raw_input=raw_input,
                user_id=user_id,
                action=action,
                target=target,
                keywords=keywords,
                output_content=f"✅ 已添加待办：{task}",
                output_data={"task": task},
                session_id=session_id,
                thread_id=thread_id,
                turn=turn
            ))

    # 默认响应
    return jsonify(build_standard_response(
        raw_input=raw_input,
        user_id=user_id,
        action=action,
        target=target,
        keywords=keywords,
        output_content=f"收到指令：{action}/{target}",
        output_data={"action": action, "target": target},
        session_id=session_id,
        thread_id=thread_id,
        turn=turn
    ))



def _handle_standard_json(standard_json: dict, user_id: str) -> dict:
    """处理标准化 JSON 输入"""
    action = standard_json.get("action", "chat")
    target = standard_json.get("target", "text")
    keywords = standard_json.get("keywords", [])
    
    user_data = get_data(user_id)
    
    if action == "schedule" and target == "task":
        if keywords:
            task = " ".join(keywords)
            user_data["todos"].append({
                "task": task,
                "completed": False,
                "created_at": datetime.now().isoformat(),
                "priority": 3
            })
            save_data(user_id, user_data)
            return jsonify({"success": True, "response": f"✅ 已添加待办：{task}", "service": "butler"})
    
    elif action == "search" and "待办" in str(keywords):
        todos = user_data.get("todos", [])
        pending = [t for t in todos if not t.get("completed", False)]
        if pending:
            response = "📝 待办事项：\n"
            for i, t in enumerate(pending[:10]):
                response += f"{i+1}. {t.get('task')}\n"
        else:
            response = "暂无待办事项"
        return jsonify({"success": True, "response": response, "service": "butler"})
    
    return jsonify({"success": True, "response": "收到指令", "service": "butler"})


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
        return jsonify({"success": True, "todos": todos, "total": len(user_data.get("todos", [])), "service": "butler"})


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
    return jsonify({"success": True, "data": user_data, "exported_at": datetime.now().isoformat(), "service": "butler"})


@api_bp.route("/butler/health", methods=["GET"])
def health():
    return jsonify({"service": "butler", "status": "healthy", "timestamp": datetime.now().isoformat(), "cache_size": len(_cache)})
