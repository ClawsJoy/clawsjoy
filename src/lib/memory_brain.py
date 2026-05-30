#!/usr/bin/env python3
"""Memory Brain - Memory Brain 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""智能记忆 - 记录和复用成功模式"""
import json
from lib.memory_simple import memory
from datetime import datetime

class MemoryBrain:
    """记忆大脑 - 学习成功经验"""
    
    @staticmethod
    def record_success(input_text, plan, result):
        """记录成功的执行模式"""
        # 提取模式（简化版）
        pattern = MemoryBrain._extract_pattern(input_text)
        
        record = {
            "pattern": pattern,
            "original": input_text,
            "plan": plan,
            "result": result,
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "hit_count": 1
        }
        
        # 检查是否已有类似模式
        existing = memory.recall_all(category='learned_patterns')
        for e in existing:
            try:
                data = json.loads(e)
                if data.get('pattern') == pattern:
                    data['hit_count'] += 1
                    data['last_used'] = datetime.now().isoformat()
                    memory.remember(json.dumps(data), category='learned_patterns')
                    print(f"📈 模式强化: {pattern} (次数: {data['hit_count']})")
                    return
            except:
                pass
        
        memory.remember(json.dumps(record), category='learned_patterns')
        print(f"🧠 学习新模式: {pattern}")
    
    @staticmethod
    def find_match(user_input):
        """查找匹配的成功模式"""
        patterns = memory.recall_all(category='learned_patterns')
        
        # 按命中次数排序（从高到低）
        matches = []
        for p in patterns[-50:]:  # 最近50条
            try:
                data = json.loads(p)
                if data.get('pattern') in user_input:
                    matches.append((data.get('hit_count', 0), data))
            except:
                pass
        
        if matches:
            matches.sort(reverse=True)
            best = matches[0][1]
            print(f"📚 命中记忆: {best.get('pattern')} (命中次数: {best.get('hit_count', 0)})")
            return best.get('plan')
        
        return None
    
    @staticmethod
    def _extract_pattern(text):
        """提取模式关键词"""
        keywords = ['大写', '反转', '统计', '编码', '解码', '空格']
        for kw in keywords:
            if kw in text:
                return f"contains_{kw}"
        return f"length_{len(text)}"
    
    @staticmethod
    def get_stats():
        """获取学习统计"""
        patterns = memory.recall_all(category='learned_patterns')
        return {
            "total_patterns": len(patterns),
            "patterns": [json.loads(p) for p in patterns[-10:]] if patterns else []
        }

memory_brain = MemoryBrain()
