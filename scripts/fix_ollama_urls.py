#!/usr/bin/env python3
"""批量修复 Ollama URL 硬编码"""

import re
from pathlib import Path

# 要修复的文件列表
files_to_fix = [
    "agents/core/autonomous_learner.py",
    "agents/core/reflection_engine.py",
    "agents/core/simple_learning_agent.py",
    "agents/core/true_intelligence_v2.py",
    "agent_core/brain_connector.py",
    "agent_core/brain_enhanced.py",
    "agent_core/brain_enhanced_v2.py",
    "intelligence/advanced_analyzer.py",
    "intelligence/unified_analyzer.py",
    "intelligence/unified_analyzer_enhanced.py",
]

# 正确的导入和用法
CORRECT_PATTERN = 'from lib.llm_config import llm_config\n\n        self.ollama_url = llm_config.get_ollama_url()'

def fix_file(file_path):
    if not Path(file_path).exists():
        print(f"   ⚠️ 文件不存在: {file_path}")
        return False
    
    content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
    
    # 检查是否有错误的硬编码
    if 'self.ollama_url = "http://smart_config.HOST' in content:
        # 添加导入
        if 'from lib.llm_config import llm_config' not in content:
            # 在文件开头添加导入
            lines = content.split('\n')
            new_lines = []
            added = False
            for i, line in enumerate(lines):
                new_lines.append(line)
                if not added and ('import' in line or 'from' in line) and i < 20:
                    new_lines.append('from lib.llm_config import llm_config')
                    added = True
            if not added:
                new_lines.insert(0, 'from lib.llm_config import llm_config')
            content = '\n'.join(new_lines)
        
        # 替换硬编码
        content = re.sub(
            r'self\.ollama_url = "http://smart_config\.HOST:str\(smart_config\.get_port\([^)]+\)[^"]*"',
            'self.ollama_url = llm_config.get_ollama_url()',
            content
        )
        
        Path(file_path).write_text(content, encoding='utf-8')
        print(f"   ✅ 已修复: {file_path}")
        return True
    
    print(f"   ⏭️ 无需修复: {file_path}")
    return False

if __name__ == "__main__":
    print("批量修复 Ollama URL 硬编码")
    print("-" * 40)
    
    for file_path in files_to_fix:
        fix_file(file_path)
    
    print("-" * 40)
    print("✅ 修复完成")
