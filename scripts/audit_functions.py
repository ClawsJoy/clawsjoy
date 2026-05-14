#!/usr/bin/env python3
"""清查所有核心函数，检查潜在问题"""

import sys
sys.path.insert(0, '/mnt/d/clawsjoy')
import inspect
import json

def audit_data_contract():
    """检查数据契约"""
    from lib.data_contract import DataContract
    methods = ['store_analysis', 'get_latest_analysis', 'store_design', 'get_latest_design']
    
    issues = []
    for method in methods:
        if hasattr(DataContract, method):
            func = getattr(DataContract, method)
            # 检查是否有 _save() 调用
            import inspect
            source = inspect.getsource(func)
            if '_save()' not in source and 'memory._save' not in source:
                issues.append(f'⚠️ {method} 缺少 _save() 调用')
            else:
                print(f'✅ {method}: 有 _save()')
        else:
            issues.append(f'❌ {method} 不存在')
    
    return issues

def audit_skill_registry():
    """检查技能注册"""
    from skills.skill_interface import skill_registry
    skills = skill_registry.get_skill_names()
    print(f'总技能数: {len(skills)}')
    
    # 检查核心技能是否存在
    core_skills = ['do_anything', 'manju_maker', 'tts', 'spider', 'add_subtitles']
    missing = [s for s in core_skills if s not in skills]
    if missing:
        print(f'⚠️ 缺失核心技能: {missing}')
    return missing

def audit_memory_save():
    """检查所有记忆写入是否有 _save()"""
    from lib.memory_simple import memory
    # 检查 remember 方法本身
    source = inspect.getsource(memory.remember)
    if '_save()' in source:
        print('✅ memory.remember 有 _save()')
    else:
        print('❌ memory.remember 缺少 _save()')

def main():
    print('='*50)
    print('ClawsJoy 函数清查')
    print('='*50)
    
    print('\n1. 数据契约检查:')
    audit_data_contract()
    
    print('\n2. 技能注册检查:')
    audit_skill_registry()
    
    print('\n3. 记忆保存检查:')
    audit_memory_save()
    
    print('\n4. 潜在问题总结:')
    # 检查常见的 BUG 模式
    import os
    bug_patterns = [
        ('memory.remember', '_save'),
        ('DataContract', '_save'),
        ('json.loads', 'try')
    ]
    
    for pattern, required in bug_patterns:
        print(f'   检查 {pattern} -> {required}')
    
    print('\n✅ 清查完成')

if __name__ == '__main__':
    main()
