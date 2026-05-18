"""ClawsJoy 统一 API 网关"""
import sys
from pathlib import Path

# 使用配置获取路径
from lib.smart_config import smart_config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from flask import Flask, jsonify, request
from flask_cors import CORS
import importlib

from src.config.settings import settings

app = Flask(__name__)
CORS(app)

_skills = {}
_workflows = {}
_legacy_skills = {}

def load_new_skills():
    skills_base = settings.ATOMIC_SKILLS_DIR
    if skills_base.exists():
        for category_dir in skills_base.iterdir():
            if category_dir.is_dir() and category_dir.name != "__pycache__":
                for skill_file in category_dir.glob("*.py"):
                    if skill_file.stem in ["__init__"]:
                        continue
                    module_path = f"src.skills.atomic.{category_dir.name}.{skill_file.stem}"
                    try:
                        module = importlib.import_module(module_path)
                        if hasattr(module, 'skill'):
                            _skills[skill_file.stem] = module.skill
                    except Exception as e:
                        print(f"⚠️ 加载 {skill_file.stem} 失败: {e}")

def load_legacy_skills():
    try:
        from lib.skill_loader_v3 import skill_loader
        for name in skill_loader.list_skills():
            _legacy_skills[name] = {'name': name, 'loader': skill_loader}
    except Exception as e:
        print(f"⚠️ 旧架构加载失败: {e}")

def load_workflows():
    workflows_base = settings.WORKFLOW_DIR
    if workflows_base.exists():
        for category_dir in workflows_base.iterdir():
            if category_dir.is_dir() and category_dir.name != "__pycache__":
                for wf_file in category_dir.glob("*.py"):
                    if wf_file.stem not in ["__init__"]:
                        module_path = f"src.skills.workflow.{category_dir.name}.{wf_file.stem}"
                        try:
                            module = importlib.import_module(module_path)
                            if hasattr(module, 'skill'):
                                _workflows[wf_file.stem] = module.skill
                        except Exception as e:
                            print(f"⚠️ 工作流 {wf_file.stem} 失败: {e}")

load_new_skills()
load_legacy_skills()
load_workflows()

print(f"📊 原子:{len(_skills)}, 旧:{len(_legacy_skills)}, 工作流:{len(_workflows)}")

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "clawsjoy", "version": "3.0"})

@app.route('/api/skills', methods=['GET'])
def list_skills():
    return jsonify({
        "atomic": list(_skills.keys()),
        "legacy": list(_legacy_skills.keys()),
        "workflows": list(_workflows.keys()),
        "total": len(_skills) + len(_legacy_skills) + len(_workflows)
    })

@app.route('/api/skills/atomic/<name>', methods=['POST'])
def execute_atomic(name):
    if name not in _skills:
        return jsonify({"error": f"技能不存在: {name}"}), 404
    return jsonify(_skills[name].execute(request.json or {}))

@app.route('/api/skills/workflow/<name>', methods=['POST'])
def execute_workflow(name):
    if name not in _workflows:
        return jsonify({"error": f"工作流不存在: {name}"}), 404
    return jsonify(_workflows[name].execute(request.json or {}))

@app.route('/api/execute', methods=['POST'])
def execute():
    data = request.json
    skill = data.get("skill")
    params = data.get("params", {})
    if skill in _skills:
        return jsonify(_skills[skill].execute(params))
    if skill in _workflows:
        return jsonify(_workflows[skill].execute(params))
    if skill in _legacy_skills:
        return jsonify(_legacy_skills[skill]['loader'].execute(skill, params))
    return jsonify({"error": f"技能不存在: {skill}"}), 404

@app.route('/api/brain', methods=['POST'])
def brain():
    from src.lib.brain import brain
    result = brain.process(request.json.get("input", ""))
    return jsonify(result)

@app.route('/api/skill/validate', methods=['POST'])
def validate():
    code = request.json.get("code", "")
    dangerous = ['os.system', 'subprocess.run', 'eval(', 'exec(', '__import__']
    issues = [p for p in dangerous if p in code]
    return jsonify({"is_safe": len(issues) == 0, "issues": issues})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=settings.GATEWAY_PORT, debug=False)

# ========== 异步技能 API ==========
@app.route('/api/async/submit', methods=['POST'])
def async_submit():
    """提交异步任务"""
    from src.lib.async_skill import async_executor
    data = request.json
    skill_name = data.get("skill")
    params = data.get("params", {})
    
    if not skill_name:
        return jsonify({"error": "需要提供技能名"}), 400
    
    task_id = async_executor.submit(skill_name, params)
    return jsonify({"task_id": task_id, "status": "pending"})

@app.route('/api/async/status/<task_id>', methods=['GET'])
def async_status(task_id):
    """查询任务状态"""
    from src.lib.async_skill import async_executor
    result = async_executor.get_result(task_id)
    return jsonify(result)

@app.route('/api/async/tasks', methods=['GET'])
def async_tasks():
    """列出所有任务"""
    from src.lib.async_skill import async_executor
    return jsonify(async_executor.list_tasks())
