#!/usr/bin/env python3
"""Self Reflection - Self Reflection 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""


import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class SelfReflection:
    """自我反思 - 像 Hermes 一样从经验中学习"""
    
    def __init__(self):
        self.reflections = []
        self.improvements = []
        self._load()
    
    def _load(self):
        ref_file = Path(f"{config_helper.get_data_root()}/autonomous/reflections.json")
        if ref_file.exists():
            with open(ref_file, 'r') as f:
                data = json.load(f)
                self.reflections = data.get('reflections', [])
                self.improvements = data.get('improvements', [])
    
    def _save(self):
        ref_file = Path(f"{config_helper.get_data_root()}/autonomous/reflections.json")
        ref_file.parent.mkdir(exist_ok=True)
        with open(ref_file, 'w') as f:
            json.dump({
                'reflections': self.reflections[-100:],
                'improvements': self.improvements,
                'updated_at': datetime.now().isoformat()
            }, f, indent=2)
    
    def reflect_on_action(self, action: str, result: Dict, context: Dict) -> Dict:
        """反思一个行动"""
        reflection = {
            "id": f"ref_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "action": action,
            "result": result,
            "context": context,
            "success": result.get('success', False),
            "timestamp": datetime.now().isoformat(),
            "lesson": self._extract_lesson(action, result)
        }

        self.reflections.append(reflection)
        self._save()

        # 如果不成功，分析原因并提出改进
        if not reflection['success']:
            improvement = self._suggest_improvement(action, result)
            if improvement:
                self.improvements.append(improvement)
                print(f"💡 改进建议: {improvement['description']}")

        return reflection
    
    def _extract_lesson(self, action: str, result: Dict) -> str:
        """提取教训"""
        if result.get('success'):
            return f"{action} 执行成功"
        else:
            error = result.get('error', result.get('result', 'unknown'))
            return f"{action} 失败: {error[:50]}"
    
    def _suggest_improvement(self, action: str, result: Dict) -> Dict:
        """提出改进建议"""
        error = result.get('error', result.get('result', ''))

        if 'timeout' in error.lower():
            return {
                "type": "timeout",
                "description": "增加超时时间",
                "action": "adjust_timeout",
                "priority": "medium"
            }
        elif 'not found' in error.lower() or '不存在' in error:
            return {
                "type": "missing",
                "description": "检查依赖是否存在",
                "action": "check_dependencies",
                "priority": "high"
            }
        elif 'connection' in error.lower():
            return {
                "type": "network",
                "description": "检查网络连接",
                "action": "retry_with_backof",
                "priority": "high"
            }

        return None
    
    def get_improvements(self) -> List[Dict]:
        """获取待实施的改进"""
        return [i for i in self.improvements if not i.get('implemented', False)]
    
    def mark_implemented(self, improvement_id: str):
        """标记改进已实施"""
        for i in self.improvements:
            if i.get('id') == improvement_id:
                i['implemented'] = True
                i['implemented_at'] = datetime.now().isoformat()
                self._save()
                return True
        return False
    
    def get_summary(self) -> Dict:
        """获取反思摘要"""
        total = len(self.reflections)
        if total == 0:
            return {"message": "暂无反思记录"}

        success = sum(1 for r in self.reflections if r.get('success', False))
        return {
            "total_reflections": total,
            "success_rate": success / total,
            "improvements_pending": len(self.get_improvements()),
            "latest_lesson": self.reflections[-1]['lesson'] if self.reflections else None
        }

self_reflection = SelfReflection()
