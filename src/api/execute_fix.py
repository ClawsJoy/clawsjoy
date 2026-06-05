#!/usr/bin/env python3
"""Execute Fix - Execute Fix 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from lib.smart_config import smart_config

# 将这个路由添加到 gateway.py 的合适位置


@app.route("/api/execute", methods=["POST"])
def execute_skill():
    """执行技能 - 自动路由"""
    data = request.get_json()
    if not data:
        return jsonify({"error": "无效的 JSON"}), 400

    skill_name = data.get("skill")
    params = data.get("params", {})

    if not skill_name:
        return jsonify({"error": "缺少 skill 参数"}), 400

    # 1. 尝试新架构原子技能
    if skill_name in _skills:
        try:
            result = _skills[skill_name].execute(params)
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    # 2. 尝试工作流
    if skill_name in _workflows:
        try:
            result = _workflows[skill_name].execute(params)
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    # 3. 尝试旧架构技能
    if skill_name in _legacy_skills:
        try:
            result = _legacy_skills[skill_name]["loader"].execute(skill_name, params)
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    # 4. 技能不存在
    return (
        jsonify(
            {
                "error": f"技能不存在: {skill_name}",
                "available_atomic": list(_skills.keys())[:20],
                "available_workflows": list(_workflows.keys()),
            }
        ),
        404,
    )
