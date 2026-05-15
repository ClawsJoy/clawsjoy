#!/usr/bin/env python3
"""自修复 Agent - 根据知识库自动解决问题"""

import json
import subprocess
import re
from pathlib import Path

class SelfHealingAgent:
    def __init__(self):
        self.knowledge_file = Path("/mnt/d/clawsjoy/data/knowledge/common_fixes.json")
        self.load_knowledge()
    
    def load_knowledge(self):
        with open(self.knowledge_file) as f:
            self.knowledge = json.load(f)
    
    def diagnose(self, error_text):
        """根据错误信息诊断问题"""
        for fix in self.knowledge["fixes"]:
            if fix["symptom"].lower() in error_text.lower():
                return fix
        return None
    
    def apply_fix(self, fix):
        """应用修复方案"""
        print(f"🔧 应用修复: {fix['problem']}")
        result = subprocess.run(fix["solution"], shell=True, capture_output=True, text=True)
        return result.returncode == 0
    
    def heal(self, error_log):
        """自愈主流程"""
        fixes_applied = []
        
        for line in error_log.split('\n'):
            fix = self.diagnose(line)
            if fix and fix not in fixes_applied:
                if self.apply_fix(fix):
                    fixes_applied.append(fix)
                    print(f"✅ 修复成功: {fix['problem']}")
        
        return fixes_applied

if __name__ == "__main__":
    healer = SelfHealingAgent()
    
    # 模拟错误日志
    test_error = "Address already in use"
    fixes = healer.heal(test_error)
    print(f"应用了 {len(fixes)} 个修复")
