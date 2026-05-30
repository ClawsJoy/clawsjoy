#!/usr/bin/env python3
"""Skill Cache - Skill Cache 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""技能缓存 - 提升性能"""
from functools import lru_cache
import importlib

class SkillCache:
    """技能缓存管理器"""
    
    @lru_cache(maxsize=128)
    def get_skill(self, skill_name: str, category: str = None):
        """获取技能（带缓存）"""
        if category:
            module_path = f"src.skills.atomic.{category}.{skill_name}"
        else:
            # 搜索所有分类
            from pathlib import Path
            for cat_dir in Path("src/skills/atomic").iterdir():
                if cat_dir.is_dir():
                    test_path = f"src.skills.atomic.{cat_dir.name}.{skill_name}"
                    try:
                        module = importlib.import_module(test_path)
                        if hasattr(module, 'skill'):
                            return module.skill
                    except:
                        continue
            return None
        
        try:
            module = importlib.import_module(module_path)
            return module.skill if hasattr(module, 'skill') else None
        except:
            return None
    
    def clear_cache(self):
        self.get_skill.cache_clear()
        print("✅ 技能缓存已清空")

skill_cache = SkillCache()
