#!/usr/bin/env python3
"""Task Decomposer - Task Decomposer 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import requests
import json
import re
from typing import List, Dict

class TaskDecomposer:
    def __init__(self):
        self.decomposition_cache = {}
    
    def decompose(self, complex_task: str) -> List[Dict]:
        if complex_task in self.decomposition_cache:
            return self.decomposition_cache[complex_task]

        # 优化 prompt，明确要求分解
        prompt = f"""请将以下复杂任务分解为 3-5 个具体的、可执行的子任务。

任务: {complex_task}

要求:
1. 每个子任务必须是可独立执行的
2. 子任务之间要有明确的依赖关系
3. 使用具体的操作描述

返回格式（只返回 JSON）:
{{
    "sub_tasks": [
        {{"name": "检查系统状态", "action": "call_health_api", "depends_on": []}},
        {{"name": "分析性能瓶颈", "action": "analyze_metrics", "depends_on": ["检查系统状态"]}},
        {{"name": "执行优化", "action": "run_optimization", "depends_on": ["分析性能瓶颈"]}},
        {{"name": "验证结果", "action": "verify_optimization", "depends_on": ["执行优化"]}}
    ]
}}"""

        try:
            resp = requests.post(
                'http://localhost:5002/api/chat',
                json={'message': prompt, 'user_role': 'system'},
                timeout=config_helper.get_timeout("default")
            )
            response = resp.json().get('response', '')

            # 提取 JSON
            match = re.search(r'\{[^{}]*"sub_tasks"[^{}]*\[.*\]\s*\}', response, re.DOTALL)
            if not match:
                match = re.search(r'\{.*\}', response, re.DOTALL)

            if match:
                data = json.loads(match.group())
                sub_tasks = data.get('sub_tasks', [])
                if len(sub_tasks) > 1:
                    self.decomposition_cache[complex_task] = sub_tasks
                    return sub_tasks
        except Exception as e:
            print(f"分解失败: {e}")

        # 降级：手动分解
        return self._manual_decompose(complex_task)
    
    def _manual_decompose(self, task: str) -> List[Dict]:
        """手动分解常见任务"""
        if "优化" in task:
            return [
                {"name": "检查系统状态", "action": "check_health", "depends_on": []},
                {"name": "清理缓存", "action": "clean_cache", "depends_on": ["检查系统状态"]},
                {"name": "同步知识库", "action": "sync_knowledge", "depends_on": ["清理缓存"]},
                {"name": "验证优化效果", "action": "verify", "depends_on": ["同步知识库"]}
            ]
        elif "备份" in task:
            return [
                {"name": "检查磁盘空间", "action": "check_disk", "depends_on": []},
                {"name": "执行备份", "action": "do_backup", "depends_on": ["检查磁盘空间"]},
                {"name": "验证备份", "action": "verify_backup", "depends_on": ["执行备份"]}
            ]
        else:
            return [{"name": task, "action": "execute", "depends_on": []}]
    
    def get_execution_order(self, sub_tasks: List[Dict]) -> List[str]:
        executed = []
        pending = [t['name'] for t in sub_tasks]

        while pending:
            for task in sub_tasks:
                if task['name'] in pending:
                    deps = task.get('depends_on', [])
                    if all(d in executed for d in deps):
                        executed.append(task['name'])
                        pending.remove(task['name'])
                        break
        return executed

task_decomposer = TaskDecomposer()
