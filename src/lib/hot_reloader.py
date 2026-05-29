from lib.smart_config import smart_config
"""技能热加载器 - 修复字典更新"""
import importlib
import sys
import time
import threading
from pathlib import Path
from src.lib.skill_version import skill_version

class HotReloader:
    def __init__(self):
        self.watchers = {}
        self.running = False
        self.check_interval = 10
        self._skills_cache = {}
        self._start_watcher()
    
    def _start_watcher(self):
        def watch():
            while self.running:
                changed = skill_version.check_changes()
                if changed:
                    for item in changed:
                        self._reload_skill(item["name"])
                time.sleep(self.check_interval)
        
        self.running = True
        thread = threading.Thread(target=watch, daemon=True)
        thread.start()
        print("🔍 热加载监控已启动")
    
    def _get_module_path(self, skill_name: str, category: str) -> str:
        return f"src.skills.atomic.{category}.{skill_name}"
    
    def _reload_skill(self, skill_name: str):
        skill_info = skill_version.get_version(skill_name)
        if not skill_info:
            return
        
        category = skill_info.get("category")
        module_path = self._get_module_path(skill_name, category)
        
        if module_path in sys.modules:
            del sys.modules[module_path]
        
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, 'skill'):
                print(f"🔄 热加载成功: {skill_name} [{category}]")
                self._skills_cache[skill_name] = module.skill
                
                # 尝试更新网关的全局技能表
                try:
                    import src.api.gateway as gateway
                    if hasattr(gateway, '_skills'):
                        gateway._skills[skill_name] = module.skill
                except:
                    pass
        except Exception as e:
            print(f"❌ 热加载失败 {skill_name}: {e}")
    
    def get_skill(self, name: str):
        return self._skills_cache.get(name)
    
    def reload_all(self):
        for name in skill_version.list_all().keys():
            self._reload_skill(name)
        print(f"✅ 已重载 {len(self._skills_cache)} 个技能")
    
    def stop(self):
        self.running = False

hot_reloader = HotReloader()
