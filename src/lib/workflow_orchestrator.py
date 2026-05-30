#!/usr/bin/env python3
"""Workflow Orchestrator - Workflow Orchestrator 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""工作流编排器 - 支持复杂多步操作"""
import json
from src.api.gateway import _skills, _workflows

class WorkflowOrchestrator:
    """工作流编排器"""
    
    def __init__(self):
        self.context = {}
    
    def execute_plan(self, plan):
        """执行计划"""
        results = []
        context = {}
        
        for i, step in enumerate(plan.get("steps", [])):
            skill_name = step.get("skill")
            params = step.get("params", {}).copy()
            
            # 替换变量 {{result}}
            for key, value in params.items():
                if isinstance(value, str) and "{{result}}" in value:
                    if context.get("result"):
                        params[key] = value.replace("{{result}}", str(context["result"]))
            
            # 执行技能
            if skill_name in _skills:
                result = _skills[skill_name].execute(params)
                results.append({
                    "step": i + 1,
                    "skill": skill_name,
                    "result": result
                })
                
                # 保存结果到上下文
                if result.get("success") and result.get("result"):
                    context["result"] = result.get("result")
                elif result.get("success") and result.get("final"):
                    context["result"] = result.get("final")
            
            elif skill_name in _workflows:
                result = _workflows[skill_name].execute(params)
                results.append({
                    "step": i + 1,
                    "skill": skill_name,
                    "result": result
                })
            
            else:
                results.append({
                    "step": i + 1,
                    "skill": skill_name,
                    "error": f"技能 {skill_name} 不存在"
                })
        
        return {
            "success": all(r.get("result", {}).get("success", False) for r in results if "error" not in r),
            "steps": len(results),
            "results": results,
            "context": context
        }

orchestrator = WorkflowOrchestrator()
