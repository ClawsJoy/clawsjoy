#!/usr/bin/env python3
"""Gateway Patch - Gateway Patch 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-5-31
"""

from lib.smart_config import smart_config

# 在现有网关中添加/修复此端点


@app.route("/api/execute", methods=["POST"])
def unified_execute():
    data = request.json
    skill_name = data.get("skill")
    params = data.get("params", {})

    if not skill_name:
        return jsonify({"error": "需要提供技能名"}), 400

    # 先尝试原子技能
    if skill_name in _skills:
        try:
            result = _skills[skill_name].execute(params)
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    # 再尝试工作流
    if skill_name in _workflows:
        try:
            result = _workflows[skill_name].execute(params)
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    # 最后尝试旧架构
    if skill_name in _legacy_skills:
        try:
            result = _legacy_skills[skill_name]["loader"].execute(skill_name, params)
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    return (
        jsonify(
            {
                "error": f"技能不存在: {skill_name}",
                "available": list(_skills.keys())[:10],
            }
        ),
        404,
    )
