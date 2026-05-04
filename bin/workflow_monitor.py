#!/usr/bin/env python3
"""Workflow 状态监控"""

import json
from pathlib import Path
import pickle

STATE_DIR = Path("/home/flybo/clawsjoy/data/workflow_states")

def list_workflows():
    """列出所有 Workflow 状态"""
    for f in STATE_DIR.glob("*.pkl"):
        with open(f, 'rb') as fp:
            state = pickle.load(fp)
        print(f"📋 {f.name}")
        print(f"   状态: {state.get('status')}")
        print(f"   进度: {state.get('current_step_index', 0)}/{len(state.get('steps', []))}")
        print()

def get_workflow_status(workflow_id):
    """获取指定 Workflow 状态"""
    for f in STATE_DIR.glob(f"*{workflow_id}*.pkl"):
        with open(f, 'rb') as fp:
            state = pickle.load(fp)
        return state
    return None

if __name__ == "__main__":
    print("=== Workflow 状态监控 ===\n")
    list_workflows()
