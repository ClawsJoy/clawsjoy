#!/usr/bin/env python3
"""Skill Warmup - Skill Warmup 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""技能预热 - 预加载常用技能"""
import importlib
from pathlib import Path
import time

class SkillWarmup:
    """技能预热器 - 提前加载常用技能"""
    
    # 高频技能列表
    HOT_SKILLS = [
        'add', 'multiply', 'to_upper', 'to_lower',
        'get_time', 'md5', 'json_parser', 'percentage'
    ]
    
    @classmethod
    def warmup(cls):
        """预热技能"""
        print("🔥 技能预热中...")
        start = time.time()
        
        loaded = 0
        for skill_name in cls.HOT_SKILLS:
            # 搜索技能文件
            for category_dir in Path("src/skills/atomic").iterdir():
                if category_dir.is_dir():
                    skill_file = category_dir / f"{skill_name}.py"
                    if skill_file.exists():
                        module_path = f"src.skills.atomic.{category_dir.name}.{skill_name}"
                        try:
                            importlib.import_module(module_path)
                            loaded += 1
                        except:
                            pass
                        break
        
        elapsed = time.time() - start
        print(f"✅ 技能预热完成: {loaded}/{len(cls.HOT_SKILLS)} 个技能 ({elapsed:.2f}s)")

# 自动预热
SkillWarmup.warmup()
