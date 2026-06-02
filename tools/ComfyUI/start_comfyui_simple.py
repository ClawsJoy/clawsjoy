#!/usr/bin/env python3
"""简化版 ComfyUI 启动器"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量
os.environ['COMFYUI_DIR'] = os.path.dirname(os.path.abspath(__file__))

# 跳过配置加载
import comfy.options
comfy.options.enable_args_parsing()

# 直接启动
import main
