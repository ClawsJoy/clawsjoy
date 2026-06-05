import sys

sys.path.insert(0, "/home/flybo/clawsjoy_v5")

import json

#!/usr/bin/env python3
import os
import re
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template_string

from core.agents.builtin.llm_agent import LLMAgent
from core.lib.smart_config import smart_config
from web.driver_api import driver_bp

app = Flask(__name__)
"""ClawsJoy Web Dashboard v3.0.00_20260515 - 修复成功率显示"""


app = Flask(__name__)

# 项目根目录
ROOT = Path(smart_config.ROOT)
LOG_FILE = os.path.join(ROOT, "logs", "active_runner.log")
MEMORY_FILE = ROOT / "data" / "memory_simple.json"


def get_success_rate_from_log():
    """从 active_runner.log 读取真实成功率"""
    if not LOG_FILE.exists():
        return {"success": 0, "failed": 0, "total": 0, "rate": 0}

    content = LOG_FILE.read_text(encoding="utf-8", errors="ignore")

    # 统计 ✅ 和 ❌
    success_count = content.count("✅ 完成")
    fail_count = content.count("❌ 失败")
    total = success_count + fail_count

    rate = (success_count / total * 100) if total > 0 else 0

    return {
        "success": success_count,
        "failed": fail_count,
        "total": total,
        "rate": round(rate, 1),
    }


def get_recent_tasks():
    """获取最近的任务列表"""
    if not LOG_FILE.exists():
        return []

    content = LOG_FILE.read_text(encoding="utf-8", errors="ignore")
    lines = content.strip().split("\n")

    tasks = []
    for line in lines[-50:]:  # 最近50行
        if "[执行]" in line:
            # 提取任务名称
            match = re.search(r"执行: \[(.*?)\] (.*?)\(", line)
            if match:
                topic = match.group(1)
                name = match.group(2).strip()

                status = (
                    "success"
                    if "✅ 完成" in line
                    else "failed" if "❌ 失败" in line else "pending"
                )

                tasks.append(
                    {
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "topic": topic,
                        "name": name,
                        "status": status,
                    }
                )

    return tasks[-20:][::-1]  # 最新的在前


def get_error_knowledge_count():
    """获取错误知识数量"""
    error_file = ROOT / "data" / "error_learning.json"
    if error_file.exists():
        try:
            with open(error_file, "r") as f:
                data = json.load(f)
                return len(data.get("learned_errors", []))
        except Exception as e:
            pass
    return 0


def get_decision_count():
    """获取决策记录数量"""
    decision_file = ROOT / "data" / "decisions.json"
    if decision_file.exists():
        try:
            with open(decision_file, "r") as f:
                data = json.load(f)
                return len(data) if isinstance(data, list) else 1
        except Exception as e:
            pass
    return 1


@app.route("/")
def index():
    """主页面"""
    stats = get_success_rate_from_log()
    recent_tasks = get_recent_tasks()
    error_count = get_error_knowledge_count()
    decision_count = get_decision_count()

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ClawsJoy 智能监控仪表板</title>
        <meta charset="utf-8">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; padding: 20px; }
            .container { max-width: 1400px; margin: 0 auto; }
            h1 { font-size: 24px; margin-bottom: 20px; color: #1a1a2e; }
            .refresh-btn { background: #4a90e2; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; margin-left: 10px; }
            .refresh-btn:hover { background: #357abd; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .stat-card { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            .stat-value { font-size: 32px; font-weight: bold; color: #1a1a2e; }
            .stat-label { font-size: 14px; color: #666; margin-top: 8px; }
            .success-rate { color: #27ae60; }
            .panel { background: white; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            .panel h3 { margin-bottom: 15px; color: #1a1a2e; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #eee; }
            th { background: #f8f9fa; font-weight: 600; }
            .status-success { color: #27ae60; font-weight: bold; }
            .status-failed { color: #e74c3c; font-weight: bold; }
            .status-pending { color: #f39c12; font-weight: bold; }
            .service-list { display: flex; flex-wrap: wrap; gap: 10px; }
            .service-tag { background: #e8f4fd; padding: 4px 12px; border-radius: 20px; font-size: 12px; color: #4a90e2; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>
                🤖 ClawsJoy 智能监控仪表板
                <button class="refresh-btn" onclick="location.reload()">🔄 刷新数据</button>
            </h1>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{{ stats.total }}</div>
                    <div class="stat-label">总任务</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value success-rate">{{ stats.rate }}%</div>
                    <div class="stat-label">任务成功率</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ error_count }}</div>
                    <div class="stat-label">错误知识</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ decision_count }}</div>
                    <div class="stat-label">决策记录</div>
                </div>
            </div>
            
            <div class="panel">
                <h3>📊 实时统计</h3>
                <div class="service-list">
                    <span class="service-tag">✅ 成功: {{ stats.success }}</span>
                    <span class="service-tag">❌ 失败: {{ stats.failed }}</span>
                    <span class="service-tag">📊 成功率: {{ stats.rate }}%</span>
                </div>
            </div>
            
            <div class="panel">
                <h3>📋 最近任务</h3>
                <table>
                    <thead>
                        <tr><th>时间</th><th>话题</th><th>任务名称</th><th>状态</th></tr>
                    </thead>
                    <tbody>
                        {% for task in recent_tasks %}
                        <tr>
                            <td>{{ task.time }}</td>
                            <td>{{ task.topic }}</td>
                            <td>{{ task.name }}</td>
                            <td class="status-{{ task.status }}">{{ "✅ 完成" if task.status == "success" else "❌ 失败" if task.status == "failed" else "⏳ 进行中" }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            
            <div class="panel">
                <h3>🕐 最新分析报告</h3>
                <p><strong>时间：</strong> {{ now }}</p>
                <p><strong>总任务：</strong> {{ stats.total }}</p>
                <p><strong>成功数：</strong> {{ stats.success }}</p>
                <p><strong>成功率：</strong> {{ stats.rate }}%</p>
                <p><strong>错误知识：</strong> {{ error_count }}</p>
                <p><strong>决策记录：</strong> {{ decision_count }}</p>
            </div>
        </div>
        
        <script>
            setTimeout(function() { location.reload(); }, 30000);
        </script>
    </body>
    </html>
    """

    return render_template_string(
        html,
        stats=stats,
        recent_tasks=recent_tasks,
        error_count=error_count,
        decision_count=decision_count,
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


@app.route("/api/stats")
def api_stats():
    """API 接口"""
    stats = get_success_rate_from_log()
    return jsonify(
        {
            "total_tasks": stats["total"],
            "success_count": stats["success"],
            "failed_count": stats["failed"],
            "success_rate": stats["rate"],
            "error_knowledge": get_error_knowledge_count(),
            "decisions": get_decision_count(),
        }
    )


# ========== 智能化 API 路由 ==========
@app.route("/api/intelligence/stats")
def intelligence_stats():
    from core.lib.smart_scheduler import smart_scheduler
    from core.lib.success_predictor import success_predictor

    return jsonify(
        {
            "predictor": success_predictor.get_stats(),
            "scheduler": smart_scheduler.get_schedule_stats(),
        }
    )


@app.route("/api/intelligence/best-tasks")
def best_tasks():
    from core.lib.success_predictor import success_predictor

    return jsonify(success_predictor.get_best_tasks(20))


@app.route("/api/intelligence/worst-tasks")
def worst_tasks():
    from core.lib.success_predictor import success_predictor

    return jsonify(success_predictor.get_worst_tasks(20))


@app.route("/api/intelligence/predict/<task_name>")
def predict_task(task_name):
    from core.lib.success_predictor import success_predictor

    return jsonify(success_predictor.predict_task_success_rate(task_name))
