#!/usr/bin/env python3
"""ClawsJoy Gateway - Full Version with Learning & Memory"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ========== 配置 ==========
DATA_DIR = Path("data")
MEMORY_FILE = DATA_DIR / "memory_simple.json"
LEARNING_FILE = DATA_DIR / "learning_data" / "learning_stats.json"
MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
(DATA_DIR / "learning_data").mkdir(parents=True, exist_ok=True)

# ========== 记忆存储函数 ==========
def load_memories(user_id):
    """加载用户记忆"""
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, 'r') as f:
            all_memories = json.load(f)
            return all_memories.get(user_id, [])
    return []

def save_memory(user_id, fact):
    """保存用户记忆"""
    memories = load_memories(user_id)
    memories.append({
        'fact': fact,
        'timestamp': datetime.now().isoformat()
    })
    
    all_memories = {}
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, 'r') as f:
            all_memories = json.load(f)
    
    all_memories[user_id] = memories[-100:]
    with open(MEMORY_FILE, 'w') as f:
        json.dump(all_memories, f, indent=2)

def search_memories(user_id, query):
    """检索相关记忆"""
    memories = load_memories(user_id)
    results = []
    for mem in memories:
        if query.lower() in mem['fact'].lower():
            results.append(mem['fact'])
    return results[:10]

# ========== 学习统计函数 ==========

def load_learning_stats():
    """加载学习统计"""
    if LEARNING_FILE.exists():
        with open(LEARNING_FILE, 'r') as f:
            data = json.load(f)
            # 兼容旧格式
            if isinstance(data, dict):
                if 'total_learnings' not in data:
                    data['total_learnings'] = data.get('learned', 0)
                if 'successful_learnings' not in data:
                    data['successful_learnings'] = 0
                if 'failed_learnings' not in data:
                    data['failed_learnings'] = 0
                return data
    return {"total_learnings": 0, "successful_learnings": 0, "failed_learnings": 0}
def save_learning_stats(stats):
    """保存学习统计"""
    with open(LEARNING_FILE, 'w') as f:
        json.dump(stats, f, indent=2)

def record_learning(fact, success=True):
    """记录学习行为"""
    stats = load_learning_stats()
    stats['total_learnings'] += 1
    if success:
        stats['successful_learnings'] += 1
    else:
        stats['failed_learnings'] += 1
    stats['last_learning'] = datetime.now().isoformat()
    save_learning_stats(stats)

# ========== 健康检查 ==========
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'clawsjoy-gateway', 'version': '4.0.0'})

@app.route('/', methods=['GET'])
def index():
    return jsonify({'service': 'ClawsJoy Gateway', 'version': '4.0.0'})

# ========== 技能列表 ==========
@app.route('/api/skills/list', methods=['GET'])
def list_skills():
    """获取技能列表"""
    try:
        from core.lib.skill_loader_v3 import skill_loader
        skills = skill_loader.list_skills()
        return jsonify({'success': True, 'total': len(skills), 'skills': skills})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ========== 智能体列表 ==========
@app.route('/api/agents/list', methods=['GET'])
def list_agents():
    """获取智能体列表"""
    agents = [
        {"name": "chat_agent", "status": "active", "version": "2.0.0"},
        {"name": "code_agent", "status": "active", "version": "1.0.0"},
        {"name": "analysis_agent", "status": "active", "version": "1.0.0"},
        {"name": "decision_agent", "status": "active", "version": "1.0.0"},
        {"name": "executor_agent", "status": "active", "version": "1.0.0"},
        {"name": "orchestrator", "status": "active", "version": "1.0.0"},
        {"name": "translate_agent", "status": "active", "version": "1.0.0"},
        {"name": "video_agent", "status": "active", "version": "1.0.0"},
        {"name": "memory_agent", "status": "active", "version": "1.0.0"},
        {"name": "director_agent", "status": "active", "version": "1.0.0"},
        {"name": "writer_agent", "status": "active", "version": "1.0.0"},
        {"name": "dialect_agent", "status": "active", "version": "1.0.0"},
        {"name": "youtube_agent", "status": "active", "version": "1.0.0"},
        {"name": "collaboration_agent", "status": "active", "version": "1.0.0"}
    ]
    return jsonify({'success': True, 'total': len(agents), 'agents': agents})

# ========== 学习统计接口 ==========
@app.route('/api/learning/stats', methods=['GET'])
def learning_stats():
    """获取学习统计"""
    stats = load_learning_stats()
    return jsonify({'success': True, 'stats': stats})

# ========== 学习接口 ==========
@app.route('/api/learning/record', methods=['POST'])
def record_learning_api():
    """记录学习"""
    data = request.json or {}
    fact = data.get('fact', '')
    success = data.get('success', True)
    
    if fact:
        record_learning(fact, success)
        return jsonify({'success': True, 'message': '学习已记录'})
    return jsonify({'success': False, 'error': 'fact required'}), 400

# ========== 增强对话（带记忆和学习） ==========
@app.route('/api/v5/enhanced/chat', methods=['POST'])
def enhanced_chat():
    """增强对话 - 带记忆和学习"""
    data = request.json or {}
    message = data.get('message', '')
    user_id = data.get('user_id', 'guest')
    
    # 检索相关记忆
    memories = search_memories(user_id, message)
    
    # 构建响应
    if memories:
        context = "根据您的记忆：\n" + "\n".join(f"- {m}" for m in memories[:3])
        response = f"{context}\n\n收到您的消息: {message}"
        # 记录学习 - 成功使用了记忆
        record_learning(f"用户 {user_id} 使用了记忆: {message}", True)
    else:
        response = f"收到您的消息: {message}"
    
    return jsonify({
        'success': True,
        'response': response,
        'agent': 'chat_agent',
        'enhanced': True,
        'memories_used': memories[:3],
        'user_id': user_id
    })

# ========== 记忆存储 ==========
@app.route('/api/v5/memory/remember', methods=['POST'])
def memory_remember():
    """存储记忆"""
    data = request.json or {}
    user_id = data.get('user_id', 'guest')
    fact = data.get('fact', '')
    
    if not fact:
        return jsonify({'success': False, 'error': 'fact required'}), 400
    
    save_memory(user_id, fact)
    record_learning(f"用户 {user_id} 学习了: {fact}", True)
    return jsonify({'success': True, 'message': '记忆已存储'})

# ========== 记忆检索 ==========
@app.route('/api/v5/memory/recall', methods=['POST'])
def memory_recall():
    """检索记忆"""
    data = request.json or {}
    user_id = data.get('user_id', 'guest')
    query = data.get('query', '')
    
    results = search_memories(user_id, query)
    return jsonify({'success': True, 'results': results})

# ========== 记忆统计 ==========
@app.route('/api/v5/memory/stats', methods=['GET'])
def memory_stats():
    """记忆统计"""
    user_id = request.args.get('user_id', 'guest')
    memories = load_memories(user_id)
    return jsonify({'success': True, 'total': len(memories)})

if __name__ == '__main__':
    port = 5002
    print(f"🚀 ClawsJoy Gateway 完整版启动在端口 {port}")
    print(f"   📝 记忆存储: data/memory_simple.json")
    print(f"   📚 学习统计: data/learning_data/learning_stats.json")
    print("=" * 50)
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
