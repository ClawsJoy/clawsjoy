 #!/usr/bin/env python3
"""导演画布专用API路由"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Blueprint, request, jsonify
import json
import time
from typing import Dict, Any, List, Optional

# 创建蓝图
canvas_bp = Blueprint('director_canvas', __name__, url_prefix='/api/director/canvas')


def get_director_agent(session_id: str):
    """获取导演Agent实例"""
    try:
        # 尝试从 wisdom_factory 获取
        from core.agents.wisdom.wisdom_factory import wisdom_factory
        agent = wisdom_factory.get_wisdom_agent('director_agent', user_id=session_id or 'default')
        if agent:
            # 注入 session_id
            if hasattr(agent, '_session_id'):
                agent._session_id = session_id
            if hasattr(agent, 'set_session'):
                agent.set_session(session_id)
            # 如果 agent 有 _agent 属性（WisdomWrapper 内部），也注入
            if hasattr(agent, '_agent') and hasattr(agent._agent, '_session_id'):
                agent._agent._session_id = session_id
            
            print(f"[Canvas] ✅ 从工厂获取Agent成功, session: {session_id}")
            return agent
    except Exception as e:
        print(f"[Canvas] 从工厂获取Agent失败: {e}")
        import traceback
        traceback.print_exc()
    # 降级：直接创建
    try:
        from agents.director_agent.agent_v4 import DirectorAgentV4
        agent = DirectorAgentV4(user_id=session_id or 'default')
        agent._session_id = session_id
        print(f"[Canvas] ⚠️ 降级到直接创建, session: {session_id}")
        return agent
    except Exception as e:
        print(f"[Canvas] 直接创建Agent失败: {e}")
        return None


@canvas_bp.route('/execute', methods=['POST'])
def execute_node():
    """
    执行单个画布节点
    """
    # ========== 根因调试：打印所有原始数据 ==========
    print("=" * 60)
    print("[根因调试] 请求方法:", request.method)
    print("[根因调试] 请求路径:", request.path)
    print("[根因调试] 请求头:", dict(request.headers))
    print("[根因调试] 原始 body (bytes):", request.data)
    print("[根因调试] 原始 body (string):", request.data.decode('utf-8') if request.data else 'None')
    
    # 尝试多种解析方式
    try:
        json_data = request.get_json()
        print("[根因调试] request.get_json():", json_data)
    except Exception as e:
        print("[根因调试] get_json() 异常:", e)
        json_data = None
    
    # 尝试手动解析
    try:
        import json
        manual_data = json.loads(request.data.decode('utf-8')) if request.data else None
        print("[根因调试] 手动 json.loads():", manual_data)
    except Exception as e:
        print("[根因调试] 手动解析异常:", e)
    print("=" * 60)
    # =============================================
    try:
        data = request.get_json()
        
        # 调试：打印收到的数据
        print(f"[Canvas] 收到请求数据: {data}")
        
        if not data:
            return jsonify({"success": False, "error": "缺少请求体"}), 400

        session_id = data.get('session_id')
        node_type = data.get('node_type')
        params = data.get('params', {})
        node_id = data.get('node_id', 'unknown')
        
        # 调试：打印提取的值
        print(f"[Canvas] session_id: {session_id}, node_type: {node_type}")

        if not session_id:
            return jsonify({
                "success": False,
                "error": "缺少 session_id",
                "received_data": data  # 返回收到的数据，帮助调试
            }), 400

        if not node_type:
            return jsonify({
                "success": False,
                "error": "缺少 node_type 参数"
            }), 400

        agent = get_director_agent(session_id)
        if not agent:
            return jsonify({
                "success": False,
                "error": "无法获取导演Agent实例"
            }), 500

        # 检查 Agent 是否有 execute_node 方法
        if not hasattr(agent, 'execute_node'):
            return jsonify({
                "success": False,
                "error": "导演Agent不支持节点执行，请更新 agent_v4.py"
            }), 500

        # 在 start_time = time.time() 之前添加
        # ===== 修复：注入 session_id 到 params =====
        params_with_session = params.copy()
        params_with_session['session_id'] = session_id
        # =========================================

        start_time = time.time()
        result = agent.execute_node(node_type, params_with_session)  # ← 使用 params_with_session
        elapsed = time.time() - start_time

        return jsonify({
            "success": True,
            "node_id": node_id,
            "node_type": node_type,
            "result": result.get("result", ""),
            "error": result.get("error"),
            "elapsed": round(elapsed, 2),
            "timestamp": time.time()
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@canvas_bp.route('/workflow/execute', methods=['POST'])
def execute_workflow():
    """
    执行完整工作流
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "缺少请求体"}), 400

        session_id = data.get('session_id')
        nodes = data.get('nodes', [])
        connections = data.get('connections', [])

        if not nodes:
            return jsonify({
                "success": False,
                "error": "没有要执行的节点"
            }), 400

        # 拓扑排序
        sorted_nodes = topological_sort(nodes, connections)
        if sorted_nodes is None:
            return jsonify({
                "success": False,
                "error": "检测到循环依赖，请检查节点连接"
            }), 400

        agent = get_director_agent(session_id)
        if not agent:
            return jsonify({
                "success": False,
                "error": "无法获取导演Agent实例"
            }), 500

        if not hasattr(agent, 'execute_node'):
            return jsonify({
                "success": False,
                "error": "导演Agent不支持节点执行"
            }), 500

        # 执行结果
        results = []
        has_error = False

        for node in sorted_nodes:
            node_id = node.get('id')
            node_type = node.get('type')
            params = node.get('params', {})

            try:
                result = agent.execute_node(node_type, params)
                results.append({
                    "node_id": node_id,
                    "node_type": node_type,
                    "success": result.get("success", False),
                    "result": result.get("result", ""),
                    "error": result.get("error")
                })
                if result.get("error"):
                    has_error = True
                    break
            except Exception as e:
                results.append({
                    "node_id": node_id,
                    "node_type": node_type,
                    "success": False,
                    "result": "",
                    "error": str(e)
                })
                has_error = True
                break

        return jsonify({
            "success": not has_error,
            "results": results,
            "total_nodes": len(sorted_nodes),
            "executed_nodes": len(results)
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@canvas_bp.route('/templates', methods=['GET'])
def get_templates():
    """获取预设模板列表"""
    templates = [
        {
            "id": "quick",
            "name": "快速短片",
            "icon": "📦",
            "description": "3步快速生成短片剧本+审查",
            "nodes": [
                {"type": "creative_input", "x": 50, "y": 80, "params": {"style": "快速", "length": "short"}},
                {"type": "script_generator", "x": 320, "y": 80, "params": {"length": "short"}},
                {"type": "quality_review", "x": 590, "y": 80, "params": {"detailed": True}}
            ],
            "connections": [
                {"from": 0, "to": 1},
                {"from": 1, "to": 2}
            ]
        },
        {
            "id": "professional",
            "name": "专业剧本",
            "icon": "🎥",
            "description": "完整专业电影剧本创作流程",
            "nodes": [
                {"type": "creative_input", "x": 50, "y": 50, "params": {"style": "深度开发", "length": "long"}},
                {"type": "character_design", "x": 50, "y": 220, "params": {"count": 4, "detail": "详细"}},
                {"type": "script_generator", "x": 320, "y": 50, "params": {"length": "long"}},
                {"type": "scene_design", "x": 320, "y": 220, "params": {"count": 8, "visualize": True}},
                {"type": "quality_review", "x": 590, "y": 50, "params": {"detailed": True, "focus": "all"}},
                {"type": "refine", "x": 590, "y": 220, "params": {"rounds": 3, "focus": "all"}},
                {"type": "export_script", "x": 860, "y": 50, "params": {"format": "fountain"}}
            ],
            "connections": [
                {"from": 0, "to": 2},
                {"from": 1, "to": 2},
                {"from": 2, "to": 4},
                {"from": 3, "to": 4},
                {"from": 4, "to": 5},
                {"from": 5, "to": 6}
            ]
        },
        {
            "id": "short_video",
            "name": "短视频",
            "icon": "📱",
            "description": "快速生成短视频脚本+分镜",
            "nodes": [
                {"type": "creative_input", "x": 50, "y": 80, "params": {"style": "爆款", "length": "short"}},
                {"type": "script_generator", "x": 320, "y": 80, "params": {"length": "short"}},
                {"type": "storyboard", "x": 590, "y": 80, "params": {"style": "竖屏"}},
                {"type": "voiceover", "x": 860, "y": 80, "params": {"emotion": "活力"}},
                {"type": "export_script", "x": 1130, "y": 80, "params": {"format": "markdown"}}
            ],
            "connections": [
                {"from": 0, "to": 1},
                {"from": 1, "to": 2},
                {"from": 2, "to": 3},
                {"from": 3, "to": 4}
            ]
        }
    ]

    return jsonify({
        "success": True,
        "templates": templates
    })


@canvas_bp.route('/node/types', methods=['GET'])
def get_node_types():
    """获取所有可用的节点类型"""
    node_types = {
        "input": [
            {"id": "creative_input", "icon": "🎬", "label": "创意输入", "desc": "一句话创意→故事大纲"},
            {"id": "material_import", "icon": "📚", "label": "素材导入", "desc": "导入已有素材/参考"}
        ],
        "processing": [
            {"id": "script_generator", "icon": "✍️", "label": "剧本生成", "desc": "叙事→格式两阶段生成"},
            {"id": "character_design", "icon": "🎭", "label": "角色设计", "desc": "深度角色档案生成"},
            {"id": "scene_design", "icon": "🎨", "label": "场景设计", "desc": "关键场景+冲突密度"},
            {"id": "storyboard", "icon": "🎬", "label": "分镜生成", "desc": "调用vision_agent生成分镜"},
            {"id": "refine", "icon": "🔄", "label": "迭代精炼", "desc": "基于反馈修改剧本"},
            {"id": "voiceover", "icon": "🎙️", "label": "配音生成", "desc": "调用audio_agent生成配音"}
        ],
        "output": [
            {"id": "quality_review", "icon": "📊", "label": "质量审查", "desc": "5维度评分+改进建议"},
            {"id": "export_script", "icon": "📤", "label": "导出剧本", "desc": "Fountain/Markdown/PDF"},
            {"id": "project_report", "icon": "📈", "label": "项目报告", "desc": "完整项目总结"},
            {"id": "one_click_film", "icon": "🎬", "label": "一键成片", "desc": "调用orchestrator全流程"}
        ]
    }

    return jsonify({
        "success": True,
        "node_types": node_types
    })


@canvas_bp.route('/workflow/save', methods=['POST'])
def save_workflow():
    """保存工作流到会话"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        workflow = data.get('workflow', {})

        if not session_id:
            return jsonify({"success": False, "error": "缺少 session_id"}), 400

        # 保存到会话
        try:
            session = session_manager.load(session_id)
            if session:
                session.set_context("canvas_workflow", workflow)
                session_manager.save(session)
                return jsonify({"success": True, "message": "工作流已保存"})
        except Exception as e:
            print(f"[Canvas] 保存到会话失败: {e}")

        # 降级：保存到文件
        workflow_dir = Path("/tmp/clawsjoy_workflows")
        workflow_dir.mkdir(exist_ok=True)
        file_path = workflow_dir / f"{session_id}_workflow.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(workflow, f, ensure_ascii=False, indent=2)

        return jsonify({
            "success": True,
            "message": "工作流已保存到本地",
            "file": str(file_path)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@canvas_bp.route('/workflow/load', methods=['GET'])
def load_workflow():
    """加载工作流"""
    try:
        session_id = request.args.get('session_id')

        if not session_id:
            return jsonify({"success": False, "error": "缺少 session_id"}), 400

        # 从会话加载
        try:
            session = session_manager.load(session_id)
            if session:
                workflow = session.get_context("canvas_workflow")
                if workflow:
                    return jsonify({"success": True, "workflow": workflow})
        except Exception as e:
            print(f"[Canvas] 从会话加载失败: {e}")

        # 从文件加载
        workflow_dir = Path("/tmp/clawsjoy_workflows")
        file_path = workflow_dir / f"{session_id}_workflow.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                workflow = json.load(f)
                return jsonify({"success": True, "workflow": workflow})

        return jsonify({
            "success": False,
            "error": "未找到保存的工作流"
        }), 404

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ========== 辅助函数 ==========

def topological_sort(nodes: List[Dict], connections: List[Dict]) -> Optional[List[Dict]]:
    """拓扑排序"""
    if not nodes:
        return []

    graph = {}
    in_degree = {}
    node_ids = [n.get('id') for n in nodes]

    for node_id in node_ids:
        graph[node_id] = []
        in_degree[node_id] = 0

    for conn in connections:
        from_id = conn.get('from')
        to_id = conn.get('to')
        if from_id in graph and to_id in graph:
            graph[from_id].append(to_id)
            in_degree[to_id] = in_degree.get(to_id, 0) + 1

    queue = [node_id for node_id in node_ids if in_degree.get(node_id, 0) == 0]
    result = []
    visited = 0

    while queue:
        node_id = queue.pop(0)
        node = next((n for n in nodes if n.get('id') == node_id), None)
        if node:
            result.append(node)
        visited += 1

        for neighbor in graph.get(node_id, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if visited != len(nodes):
        return None

    return result


# ========== 健康检查 ==========
@canvas_bp.route('/health', methods=['GET'])
def canvas_health():
    """画布模块健康检查"""
    return jsonify({
        "success": True,
        "module": "director_canvas",
        "status": "healthy",
        "timestamp": time.time()
    })
