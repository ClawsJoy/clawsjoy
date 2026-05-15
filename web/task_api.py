"""定时任务 API"""
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from pathlib import Path

app = Flask(__name__)
CORS(app)

from skills.scheduler import scheduler

@app.route('/api/tasks', methods=['GET'])
def list_tasks():
    return jsonify({"tasks": scheduler.list_tasks()})

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.json
    result = scheduler.add_task(
        data.get('name'),
        data.get('schedule'),
        data.get('type', 'skill'),
        data.get('params')
    )
    return jsonify(result)

@app.route('/api/tasks/<name>', methods=['DELETE'])
def remove_task(name):
    result = scheduler.remove_task(name)
    return jsonify(result)

@app.route('/api/tasks/history', methods=['GET'])
def task_history():
    log_file = Path("logs/task_history.jsonl")
    history = []
    if log_file.exists():
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    history.append(json.loads(line))
                except:
                    pass
    return jsonify({"history": history[-50:]})

if __name__ == '__main__':
    print("⏰ 定时任务 API 启动: http://localhost:5023")
    app.run(host='0.0.0.0', port=5023, debug=False)
