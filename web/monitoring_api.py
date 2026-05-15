"""监控数据 API - 为 Dashboard 提供实时数据"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from flask import Flask, jsonify, request
from flask_cors import CORS
from lib.unified_config import config
from lib.memory_simple import memory
from lib.skill_loader_v3 import skill_loader
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/api/monitoring/status', methods=['GET'])
def monitoring_status():
    """系统状态"""
    return jsonify({
        "gateway": {"status": "ok", "port": config.get_port('gateway')},
        "file_service": {"status": "ok", "port": config.get_port('file')},
        "multi_agent": {"status": "ok", "port": config.get_port('multi_agent')},
        "doc_generator": {"status": "ok", "port": config.get_port('doc')},
        "web_dashboard": {"status": "ok", "port": config.get_port('web')}
    })

@app.route('/api/monitoring/memory', methods=['GET'])
def monitoring_memory():
    """记忆统计"""
    stats = {}
    categories = ['workflow_outcome', 'error_knowledge', 'user_feedback', 
                  'executed_decisions', 'intelligence_analysis', 'system_monitoring']
    for cat in categories:
        stats[cat] = len(memory.recall_all(category=cat))
    return jsonify(stats)

@app.route('/api/monitoring/skills', methods=['GET'])
def monitoring_skills():
    """技能统计"""
    categories = skill_loader.get_categories()
    stats = {
        cat: info['count'] for cat, info in categories.items()
    }
    stats['total'] = len(skill_loader.list_skills())
    
    # 添加分类详情
    stats['categories'] = categories
    
    return jsonify(stats)

@app.route('/api/monitoring/analyses', methods=['GET'])
def monitoring_analyses():
    """分析报告"""
    limit = request.args.get('limit', 10, type=int)
    analyses = memory.recall_all(category='intelligence_analysis')
    result = []
    for a in analyses[-limit:]:
        try:
            data = json.loads(a)
            result.append(data)
        except:
            continue
    return jsonify(result)

@app.route('/api/monitoring/tasks', methods=['GET'])
def monitoring_tasks():
    """任务记录"""
    limit = request.args.get('limit', 20, type=int)
    tasks = memory.recall_all(category='workflow_outcome')
    result = []
    for t in tasks[-limit:]:
        result.append({
            "raw": t[:100],
            "success": "成功" in t
        })
    return jsonify(result)

@app.route('/api/monitoring/dashboard', methods=['GET'])
def monitoring_dashboard():
    """仪表板汇总数据"""
    analyses = memory.recall_all(category='intelligence_analysis')
    latest = {}
    if analyses:
        try:
            latest = json.loads(analyses[-1])
        except:
            pass
    
    return jsonify({
        "status": monitoring_status().json,
        "memory_stats": monitoring_memory().json,
        "skills_stats": monitoring_skills().json,
        "latest_analysis": latest,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = 5021
    print(f"📊 监控 API 启动: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
