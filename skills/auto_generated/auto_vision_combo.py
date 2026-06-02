#!/usr/bin/env python3
"""Auto Vision Combo - Auto Vision Combo 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


from lib.skill_loader_v3 import skill_loader


class AutoVisionCombo:
    """自动生成的组合技能 - 标准化参数传递"""

    name = "auto_vision_combo"
    description = "自动组合技能: vision → translate"
    version = "1.0.0"
    category = "auto_generated"

    def execute(self, params):
        """执行组合技能，自动分发参数"""
        results = {}

        # 1. 执行 vision（需要 image_path）
        image_path = params.get("image_path") or params.get("image", "")
        if image_path:
            vision_result = skill_loader.execute("vision", {"image_path": image_path})
            results["vision"] = vision_result.get("result", vision_result)
        else:
            results["vision"] = {"success": False, "error": "image_path required"}

        # 2. 执行 translate（需要 text）
        text = params.get("text", "")
        if text:
            translate_result = skill_loader.execute("translate", {"text": text, "target": params.get("target", "zh")})
            results["translate"] = translate_result.get("result", translate_result)
        elif results["vision"] and isinstance(results["vision"], dict):
            # 从 vision 结果中提取文本
            vision_text = results["vision"].get("result") or results["vision"].get("description", "")
            if vision_text:
                translate_result = skill_loader.execute("translate", {"text": str(vision_text), "target": params.get("target", "zh")})
                results["translate"] = translate_result.get("result", translate_result)
            else:
                results["translate"] = {"success": False, "error": "no text from vision"}
        else:
            results["translate"] = {"success": False, "error": "text required"}

        # 3. 综合结果
        all_success = all(r.get("success", False) for r in results.values() if isinstance(r, dict))

        return {
            "success": all_success,
            "result": results,
            "composed_of": ["vision", "translate"]
        }


# 全局实例
skill = AutoVisionCombo()
