#!/usr/bin/env python3
"""强制使用新加载器的网关启动器"""
import sys
import os

# 设置路径
from lib.smart_config import smart_config
sys.path.insert(0, 'str(smart_config.ROOT)')
os.chdir('str(smart_config.ROOT)')

# 清除缓存
import importlib
for module in list(sys.modules.keys()):
    if 'skill_loader' in module:
        del sys.modules[module]

# 导入新加载器
from lib.skill_loader_v3 import skill_loader
print(f"预加载技能数: {len(skill_loader.list_skills())}")

# 启动原网关
from agent_gateway_web import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=False)
