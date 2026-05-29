"""学习 API - 集成到主网关"""

from flask import Blueprint, request, jsonify
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.learner.self_learning_coordinator import SelfLearningCoordinator, ScenarioGenerator

learning_bp = Blueprint('learning', __name__, url_prefix='/api/learning')

_learner = None
_generator = None

def get_learner():
    global _learner
    if _learner is None:
        _learner = SelfLearningCoordinator()
    return _learner

def get_generator():
    global _generator
    if _generator is None:
        _generator = ScenarioGenerator()
    return _generator

@learning_bp.route('/chat', methods=['POST'])
def chat():
    """对话接口（兼容 web_learner）"""
    data = request.get_json() or {}
    message = data.get('message', '')
    
    learner = get_learner()
    result = learner.learn_from_scenario({
        'type': 'chat',
        'input': message,
        'expected': '正常回复'
    })
    
    return jsonify({
        'response': result.get('response', '处理完成'),
        'skill': 'learning_agent',
        'success': result.get('success', False)
    })

@learning_bp.route('/stats', methods=['GET'])
def stats():
    """统计接口"""
    learner = get_learner()
    return jsonify({
        'stats': learner.stats,
        'skills_count': len(get_generator().skills)
    })

@learning_bp.route('/trigger', methods=['POST'])
def trigger_learning():
    """手动触发学习"""
    data = request.get_json() or {}
    scenario = data.get('scenario', {})
    
    if not scenario:
        return jsonify({'error': 'scenario required'}), 400
    
    learner = get_learner()
    result = learner.learn_from_scenario(scenario)
    
    return jsonify({'success': True, 'result': result})

def register_learning_api(app):
    app.register_blueprint(learning_bp)
    print("   ✅ 学习 API 已集成")
