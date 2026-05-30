#!/usr/bin/env python3
"""Paths - Paths 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""统一路径配置"""
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_ROOT = PROJECT_ROOT / "src"

# 使用环境变量或默认值
CLAWSJOY_ROOT = os.environ.get("CLAWSJOY_ROOT", str(PROJECT_ROOT))

def get_root():
    return Path(CLAWSJOY_ROOT)

def get_skills_dir():
    return get_root() / "src/skills"

def get_atomic_skills_dir():
    return get_skills_dir() / "atomic"
