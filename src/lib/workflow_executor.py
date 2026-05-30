#!/usr/bin/env python3
"""Workflow Executor - Workflow Executor 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""工作流执行器"""
import re
from src.lib.skill_loader_v3 import skill_loader
from src.lib.skill_registry import skill_registry

class WorkflowExecutor:
    def execute(self, workflow_name: str, input_params: dict) -> dict:
        workflow = skill_registry.workflows.get(workflow_name)
        if not workflow:
            return {"success": False, "error": f"工作流不存在: {workflow_name}"}
        
        context = {"input": input_params}
        results = {}
        
        for step in workflow.steps:
            skill_name = step["skill"]
            params = self._resolve_params(step.get("params", {}), context, results)
            result = skill_loader.execute(skill_name, params)
            
            output_key = step.get("output", skill_name)
            results[output_key] = result
            
            if not result.get("success"):
                return {"success": False, "error": f"步骤失败: {skill_name}", "detail": result}
        
        return {"success": True, "workflow": workflow_name, "results": results}
    
    def _resolve_params(self, params: dict, context: dict, results: dict) -> dict:
        resolved = {}
        for key, value in params.items():
            if isinstance(value, str):
                value = value.replace("{input.topic}", str(context.get("input", {}).get("topic", "")))
                if "{steps.script.output.script}" in value:
                    script = results.get("script", {}).get("script", "")
                    value = value.replace("{steps.script.output.script}", script)
                if "{steps.audio.output.audio_path}" in value:
                    audio_path = results.get("audio", {}).get("audio_path", "")
                    value = value.replace("{steps.audio.output.audio_path}", audio_path)
            resolved[key] = value
        return resolved

workflow_executor = WorkflowExecutor()
