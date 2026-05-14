"""智能代码补齐 - 对标 Continue"""
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

from agent_core.brain_enhanced import brain as brain_core

class CodeCompleter:
    """智能代码补齐器"""
    
    def __init__(self):
        self.context_memory = []
        self.completion_stats = defaultdict(lambda: {'used': 0, 'accepted': 0})
        self.load_history()
        
        print("\n" + "="*60)
        print("🤖 智能代码补齐系统")
        print("="*60)
    
    def load_history(self):
        """加载历史"""
        history_file = Path("data/completion_history.json")
        if history_file.exists():
            with open(history_file, 'r') as f:
                data = json.load(f)
                self.context_memory = data.get('contexts', [])
                self.completion_stats = data.get('stats', defaultdict(lambda: {'used': 0, 'accepted': 0}))
    
    def save_history(self):
        """保存历史"""
        history_file = Path("data/completion_history.json")
        with open(history_file, 'w') as f:
            json.dump({
                'contexts': self.context_memory[-500:],
                'stats': dict(self.completion_stats)
            }, f, indent=2)
    
    def get_context_from_file(self, file_path, line_num, window=5):
        """获取文件上下文"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            start = max(0, line_num - window)
            end = min(len(lines), line_num + window)
            
            context = {
                'file': file_path,
                'line': line_num,
                'before': ''.join(lines[start:line_num]) if line_num > 0 else '',
                'after': ''.join(lines[line_num:end]) if line_num < len(lines) else '',
                'current_line': lines[line_num] if line_num < len(lines) else ''
            }
            return context
        except Exception as e:
            return {'error': str(e)}
    
    def suggest_completion(self, partial_code, file_type='python'):
        """智能补齐建议"""
        suggestions = []
        
        # 1. 基于模式的补齐
        patterns = {
            'def ': r'def (\w+)\(',
            'class ': r'class (\w+)',
            'import ': r'import (\w+)',
            'from ': r'from (\w+) import',
            'self.': r'self\.(\w+)',
            'python3 ': r'python3 (\w+\.py)'
        }
        
        for pattern_type, pattern in patterns.items():
            if partial_code.startswith(pattern_type):
                matches = re.findall(pattern, partial_code + ' ')
                if matches:
                    suggestions.append({
                        'completion': partial_code + matches[0],
                        'type': pattern_type,
                        'confidence': 0.8
                    })
        
        # 2. 从历史命令中学习
        for ctx in self.context_memory[-20:]:
            if partial_code.lower() in ctx.get('command', '').lower():
                suggestions.append({
                    'completion': ctx.get('command', ''),
                    'type': 'historical',
                    'confidence': 0.6
                })
        
        # 3. 从大脑获取经验
        experiences = brain_core.knowledge.get('experiences', [])
        for exp in experiences[-20:]:
            action = exp.get('action', '')
            if partial_code.lower() in action.lower():
                suggestions.append({
                    'completion': action,
                    'type': 'brain_memory',
                    'confidence': 0.7
                })
        
        # 去重
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            if s['completion'] not in seen:
                seen.add(s['completion'])
                unique_suggestions.append(s)
        
        return unique_suggestions[:5]
    
    def record_completion(self, command, accepted, context=''):
        """记录补齐使用情况"""
        self.completion_stats[command]['used'] += 1
        if accepted:
            self.completion_stats[command]['accepted'] += 1
        
        self.context_memory.append({
            'command': command,
            'accepted': accepted,
            'context': context,
            'timestamp': datetime.now().isoformat()
        })
        
        # 记录到大脑
        brain_core.record_experience(
            agent="code_completer",
            action="suggest",
            result={"accepted": accepted},
            context=command[:100]
        )
        
        self.save_history()
    
    def get_smart_suggestions(self, current_input):
        """获取智能建议"""
        suggestions = self.suggest_completion(current_input)
        
        # 排序：先高置信度，再常用
        for s in suggestions:
            stats = self.completion_stats.get(s['completion'], {'used': 0, 'accepted': 0})
            s['popularity'] = stats['used']
        
        suggestions.sort(key=lambda x: (x['confidence'], x.get('popularity', 0)), reverse=True)
        
        return suggestions

if __name__ == "__main__":
    completer = CodeCompleter()
    
    # 测试
    test_inputs = ["python3 ", "def ", "import ", "curl "]
    
    for inp in test_inputs:
        print(f"\n输入: {inp}")
        suggestions = completer.get_smart_suggestions(inp)
        for s in suggestions[:3]:
            print(f"  → {s['completion']} (置信度 {s['confidence']:.0%})")
