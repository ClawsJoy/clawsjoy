#!/usr/bin/env python3
"""Skills 热加载模块 - 无需重启即可加载新 Skill"""

import os
import sys
import time
import importlib
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

SKILLS_DIR = Path("/home/flybo/clawsjoy/skills")

class SkillHotReloader:
    """Skills 热加载器"""
    
    def __init__(self):
        self.skills_cache = {}
        self.last_modified = {}
        self._scan_skills()
    
    def _scan_skills(self):
        """扫描并加载所有 Skills"""
        for skill_dir in SKILLS_DIR.iterdir():
            if skill_dir.is_dir() and (skill_dir / "execute.py").exists():
                skill_name = skill_dir.name
                exec_file = skill_dir / "execute.py"
                mtime = exec_file.stat().st_mtime
                
                if skill_name not in self.last_modified or self.last_modified[skill_name] != mtime:
                    self._load_skill(skill_name, exec_file)
                    self.last_modified[skill_name] = mtime
    
    def _load_skill(self, skill_name, exec_file):
        """动态加载 Skill"""
        spec = importlib.util.spec_from_file_location(f"{skill_name}_exec", exec_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.skills_cache[skill_name] = module
        print(f"✅ 热加载 Skill: {skill_name}")
    
    def execute(self, skill_name, params):
        """执行 Skill"""
        if skill_name not in self.skills_cache:
            self._scan_skills()
        if skill_name not in self.skills_cache:
            return {"error": f"Skill '{skill_name}' not found"}
        return self.skills_cache[skill_name].execute(params)
    
    def list_skills(self):
        """列出所有 Skills"""
        self._scan_skills()
        return list(self.skills_cache.keys())
    
    def watch(self):
        """监听文件变化"""
        class Handler(FileSystemEventHandler):
            def on_modified(self, event):
                if event.src_path.endswith("execute.py"):
                    print(f"🔄 检测到变化: {event.src_path}")
                    loader._scan_skills()
        
        observer = Observer()
        observer.schedule(Handler(), str(SKILLS_DIR), recursive=True)
        observer.start()
        print(f"👀 监听 Skills 目录: {SKILLS_DIR}")
        return observer

if __name__ == "__main__":
    loader = SkillHotReloader()
    print(f"已加载 Skills: {loader.list_skills()}")
    
    # 示例：执行 Skill
    result = loader.execute("auth", {"action": "health"})
    print(f"auth: {result}")
