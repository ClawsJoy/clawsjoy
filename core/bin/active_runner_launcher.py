#!/usr/bin/env python3
"""active_runner 启动器 - 使用绝对路径"""

import sys
import os

# 设置工作目录
os.chdir('/mnt/d/clawsjoy_clean')
sys.path.insert(0, '/mnt/d/clawsjoy_clean')

# 直接导入并执行
from bin.active_runner_v3_0_01_20260517 import main

if __name__ == "__main__":
    main()
