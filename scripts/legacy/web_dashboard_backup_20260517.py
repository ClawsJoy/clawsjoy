#!/usr/bin/env python3
"""ClawsJoy Web 管理面板"""

from flask import Flask, jsonify, render_template_string
import requests
from lib.smart_config import smart_config

app = Flask(__name__)

# HTML 模板
DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>ClawsJoy 管理面板</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f2f5; }
        h1 { color: #1a73e8; }
        .card { background: white; border-radius: 8px; padding: 20px; margin: 10px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }
        .stat-number { font-size: 36px; font-weight: bold; }
        .stat-label { font-size: 14px; opacity: 0.9; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f8f9fa; }
        .healthy { color: green; }
        .unhealthy { color: red; }
        .refresh { background: #1a73e8; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <h1>🤖 ClawsJoy 管理面板</h1>
    <button class="refresh" onclick="location.reload()">🔄 刷新</button>
    
    <div class="card">
        <h2>📊 系统统计</h2>
        <div class="stats" id="stats"></div>
    </div>
    
    <div class="card">
        <h2>📋 Agent 列表</h2>
        <table id="agents">
            <thead><tr><th>名称</th><th>类型</th><th>状态</th><th>能力</th></tr></thead>
            <tbody></tbody>
        </table>
    </div>
    
    <div class="card">
        <h2>📡 服务状态</h2>
        <table id="services">
            <thead><tr><th>服务</th><th>端口</th><th>状态</th></tr></thead>
            <tbody></tbody>
        </table>
    </div>
    
    <script>
        async function loadData() {
            try {
                const agentsRes = await fetch('/api/agents/info');
                const agentsData = await agentsRes.json();
                document.getElementById('stats').innerHTML = `
                    <div class="stat-card"><div class="stat-number">${agentsData.stats?.total || 0}</div><div class="stat-label">Agent 总数</div></div>
                    <div class="stat-card"><div class="stat-number">${agentsData.stats?.core || 0}</div><div class="stat-label">核心 Agent</div></div>
                    <div class="stat-card"><div class="stat-number">${agentsData.stats?.custom || 0}</div><div class="stat-label">自定义 Agent</div></div>
                `;
                
                const agentsTable = document.querySelector('#agents tbody');
                agentsTable.innerHTML = '';
                for (const [name, info] of Object.entries(agentsData.agents || {})) {
                    agentsTable.innerHTML += `<tr><td>${name}</td><td>${info.type}</td><td class="healthy">✅ 活跃</td><td>${(info.capabilities || []).join(', ')}</td></tr>`;
                }
                
                const servicesRes = await fetch('/api/services');
                const servicesData = await servicesRes.json();
                const servicesTable = document.querySelector('#services tbody');
                servicesTable.innerHTML = '';
                for (const [name, svc] of Object.entries(servicesData.services || {})) {
                    servicesTable.innerHTML += `<tr><td>${name}</td><td>${svc.port}</td><td class="healthy">✅ ${svc.status}</td></tr>`;
                }
            } catch(e) { console.error(e); }
        }
        loadData();
        setInterval(loadData, 30000);
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/health')
def health():
    return jsonify({"status": "ok", "service": "web-dashboard"})

if __name__ == '__main__':
    port = smart_config.get_port('web')
    print(f"🌐 Web 面板启动: http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
