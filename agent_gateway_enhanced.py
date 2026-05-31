#!/usr/bin/env python3
"""ClawsJoy Gateway - 完整版主网关"""

import json
import sys
import os
import re
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

from core.lib.unified_config import unified_config
from core.lib.smart_active_service import smart_service

app = Flask(__name__)
CORS(app)

# ========== 配置 ==========
DATA_DIR = Path("data")
MEMORY_FILE = DATA_DIR / "memory_simple.json"
LEARNING_FILE = DATA_DIR / "learning_data" / "learning_stats.json"
MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "learning_data").mkdir(parents=True, exist_ok=True)

# ========== 记忆函数 ==========
def load_memories(user_id):
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, 'r') as f:
            all_memories = json.load(f)
            return all_memories.get(user_id, [])
    return []

def save_memory(user_id, fact):
    memories = load_memories(user_id)
    memories.append({'fact': fact, 'timestamp': datetime.now().isoformat()})
    all_memories = {}
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, 'r') as f:
            all_memories = json.load(f)
    all_memories[user_id] = memories[-100:]
    with open(MEMORY_FILE, 'w') as f:
        json.dump(all_memories, f, indent=2)

def search_memories(user_id, query):
    memories = load_memories(user_id)
    results = []
    for m in memories:
        fact = m.get('fact', '')
        if '名字' in query and '叫' in fact:
            results.append(fact)
        elif query.lower() in fact.lower():
            results.append(fact)
    return results[:10]

# ========== 学习函数 ==========
def load_learning_stats():
    if LEARNING_FILE.exists():
        with open(LEARNING_FILE, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict):
                if 'total_learnings' not in data:
                    data['total_learnings'] = data.get('learned', 0)
                return data
    return {"total_learnings": 0, "successful_learnings": 0, "failed_learnings": 0}

def record_learning(fact, success=True):
    stats = load_learning_stats()
    stats['total_learnings'] = stats.get('total_learnings', 0) + 1
    if success:
        stats['successful_learnings'] = stats.get('successful_learnings', 0) + 1
    else:
        stats['failed_learnings'] = stats.get('failed_learnings', 0) + 1
    with open(LEARNING_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

# ========== 用户状态 ==========
USER_STATES = {}

def get_user_state(user_id):
    if user_id not in USER_STATES:
        USER_STATES[user_id] = {}
    return USER_STATES[user_id]

def extract_user_info(message, user_id):
    state = get_user_state(user_id)
    name_match = re.search(r"我叫([\u4e00-\u9fa5]{2,4})", message)
    if name_match:
        name = name_match.group(1)
        state["name"] = name
        save_memory(user_id, f"用户名字: {name}")
        save_memory(user_id, f"用户说: 我叫{name}")
        return True
    return False

def answer_from_state(message, user_id):
    """从记忆中回答问题 - 直接从文件读取"""
    if "我叫什么名字" in message or "我的名字" in message:
        memories = load_memories(user_id)
        for m in memories:
            fact = m.get("fact", "")
            if "用户名字:" in fact:
                name = fact.replace("用户名字: ", "")
                if name:
                    return f"您叫{name}呀，我记着呢！"
            if "用户说: 我叫" in fact:
                start = fact.find("我叫")
                if start != -1:
                    name = fact[start+2:start+6].strip("，。！？")
                    if name:
                        return f"您叫{name}呀，我记着呢！"
        return "您还没告诉我您的名字呢。您可以说'我叫XXX'告诉我哦~"
    return None

# ========== 基础路由 ==========
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'clawsjoy-gateway', 'version': '5.0.0'})

@app.route('/', methods=['GET'])
def index():
    return jsonify({'service': 'ClawsJoy Gateway', 'version': '5.0.0'})

# ========== 技能和智能体 ==========
@app.route('/api/skills/list', methods=['GET'])
def list_skills():
    try:
        from core.lib.unified_skill_manager import unified_manager
        skills = unified_manager.list_all()
        return jsonify({'success': True, 'total': len(skills), 'skills': skills})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/agents/list', methods=['GET'])
def list_agents():
    agents = [
        {"name": "chat_agent", "status": "active", "version": "2.0.0"},
        {"name": "code_agent", "status": "active", "version": "1.0.0"},
        {"name": "analysis_agent", "status": "active", "version": "1.0.0"},
        {"name": "decision_agent", "status": "active", "version": "1.0.0"},
        {"name": "executor_agent", "status": "active", "version": "1.0.0"},
        {"name": "orchestrator", "status": "active", "version": "1.0.0"},
        {"name": "translate_agent", "status": "active", "version": "2.0.0"},
        {"name": "vision_agent", "status": "active", "version": "1.0.0"},
        {"name": "memory_agent", "status": "active", "version": "1.0.0"},
    ]
    return jsonify({'success': True, 'total': len(agents), 'agents': agents})

# ========== 增强对话 ==========
@app.route('/api/v5/enhanced/chat', methods=['POST'])
def enhanced_chat():
    data = request.json or {}
    message = data.get('message', '')
    user_id = data.get('user_id', 'guest')
    
    # 提取用户信息
    extract_user_info(message, user_id)
    
    # 从状态回答
    direct_answer = answer_from_state(message, user_id)
    if direct_answer:
        return jsonify({
            "success": True,
            "response": direct_answer,
            "agent": "state_manager",
            "enhanced": True,
            "user_id": user_id
        })
    
    # 调用 LLM 服务
    try:
        import requests
        resp = requests.post(
            "http://localhost:5012/chat",
            json={"message": message},
            timeout=60
        )
        if resp.status_code == 200:
            response = resp.json().get('response', '')
        else:
            response = f"服务异常: {resp.status_code}"
    except Exception as e:
        response = f"服务繁忙: {e}"
    
    save_memory(user_id, f"用户说: {message}")
    save_memory(user_id, f"ClawsJoy说: {response[:200]}")
    record_learning(f"对话: {user_id} -> {message[:30]}", True)
    
    return jsonify({
        "success": True,
        "response": response,
        "agent": "chat_agent",
        "enhanced": True,
        "user_id": user_id
    })

# ========== 记忆路由 ==========
@app.route('/api/v5/memory/remember', methods=['POST'])
def memory_remember():
    data = request.json or {}
    user_id = data.get('user_id', 'guest')
    fact = data.get('fact', '')
    if not fact:
        return jsonify({'success': False, 'error': 'fact required'}), 400
    save_memory(user_id, fact)
    record_learning(f"用户 {user_id} 学习了: {fact}", True)
    return jsonify({'success': True, 'message': '记忆已存储'})

@app.route('/api/v5/memory/recall', methods=['POST'])
def memory_recall():
    data = request.json or {}
    user_id = data.get('user_id', 'guest')
    query = data.get('query', '')
    results = search_memories(user_id, query)
    return jsonify({'success': True, 'results': results})

@app.route('/api/v5/memory/stats', methods=['GET'])
def memory_stats():
    user_id = request.args.get('user_id', 'guest')
    memories = load_memories(user_id)
    return jsonify({'success': True, 'total': len(memories)})

# ========== 学习路由 ==========
@app.route('/api/learning/stats', methods=['GET'])
def learning_stats():
    stats = load_learning_stats()
    return jsonify({'success': True, 'stats': stats})

@app.route('/api/learning/record', methods=['POST'])
def record_learning_api():
    data = request.json or {}
    fact = data.get('fact', '')
    success = data.get('success', True)
    if fact:
        record_learning(fact, success)
        return jsonify({'success': True, 'message': '学习已记录'})
    return jsonify({'success': False, 'error': 'fact required'}), 400

# ========== 向量服务 ==========
@app.route('/api/vector/stats', methods=['GET'])
def vector_stats():
    try:
        from core.lib.vector_knowledge_center import vector_knowledge_center
        stats = {
            'skills': 0,
            'agents': 0,
            'routes': 0,
            'memories': 0,
            'documents': 0
        }
        if hasattr(vector_knowledge_center, 'collections'):
            for name, col in vector_knowledge_center.collections.items():
                if name in stats:
                    stats[name] = col.count()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== 俱乐部 ==========
@app.route('/api/club/stats', methods=['GET'])
def club_stats():
    try:
        from core.butler_club.center import butler_club
        return jsonify({'success': True, 'stats': butler_club.get_stats()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== 工作流 ==========
@app.route('/api/workflows/list', methods=['GET'])
def list_workflows():
    workflows_dir = Path("workflows")
    workflows = []
    if workflows_dir.exists():
        for f in workflows_dir.glob("*.json"):
            workflows.append({'name': f.stem, 'file': f.name})
    return jsonify({'success': True, 'total': len(workflows), 'workflows': workflows})

# ========== 热重载 ==========
@app.route('/api/skills/reload', methods=['POST'])
def reload_skills():
    try:
        from core.lib.unified_skill_manager import unified_manager
        unified_manager.reload()
        return jsonify({'success': True, 'message': '技能已重载'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hot-reload/status', methods=['GET'])
def hot_reload_status():
    return jsonify({'success': True, 'status': 'active', 'watchers': ['config', 'skills']})

if __name__ == '__main__':
    port = unified_config.get("services.gateway.port", 5002)
    smart_service.start()
    print("=" * 50)
    print(f"🚀 ClawsJoy Gateway 启动在端口 {port}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
