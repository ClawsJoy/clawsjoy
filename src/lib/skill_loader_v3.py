"""技能加载器 - 兼容层"""
import sys
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
from lib.skill_loader_v3 import skill_loader as _loader

def get_loader():
    return _loader

skill_loader = _loader
