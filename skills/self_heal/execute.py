#!/usr/bin/env python3
"""自愈技能 - 固化版"""

import subprocess
import sys
sys.path.insert(0, '/mnt/d/clawsjoy')

def execute(params=None):
    result = subprocess.run('./bin/auto_heal.sh', shell=True, capture_output=True, text=True)
    return {'success': result.returncode == 0, 'output': result.stdout, 'skill': 'self_heal'}

if __name__ == "__main__":
    print(execute())
