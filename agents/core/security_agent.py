#!/usr/bin/env python3
"""安全员 Agent - 代码安全、配置安全、内容审核"""

import os
import re
import json
import subprocess
from pathlib import Path
from datetime import datetime

class SecurityAgent:
    def __init__(self):
        self.workspace = Path("/mnt/d/clawsjoy")
        self.report_file = self.workspace / "data/security_report.json"
        self.audit_log = self.workspace / "logs/security_audit.log"
        
        # 敏感模式
        self.sensitive_patterns = {
            "api_key": r'(api[_-]?key|apikey|access[_-]?key|secret[_-]?key)\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
            "token": r'(token|access_token|refresh_token)\s*[:=]\s*["\']?([a-zA-Z0-9_\-\.]{20,})["\']?',
            "password": r'(password|passwd|pwd)\s*[:=]\s*["\']?([^"\']{4,})["\']?',
            "private_key": r'-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----',
            "client_secret": r'client_secret["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,})["\']?',
            "unsplash_key": r'ijXPXhcaX2k5neNoQAzN1cw8DJl3i9gx8FlRnzspqKs',
            "youtube_key": r'youtube.*client_secret["\']?\s*[:=]\s*["\']?([^"\']+)'
        }
        
        self.load_data()
    
    def load_data(self):
        self.report = {}
    
    def log(self, msg, level="INFO"):
        timestamp = datetime.now().isoformat()
        with open(self.audit_log, 'a') as f:
            f.write(f"[{timestamp}] [{level}] {msg}\n")
        print(f"[{level}] {msg}")
    
    def scan_gitignore(self):
        """检查 .gitignore 配置"""
        gitignore_path = self.workspace / ".gitignore"
        issues = []
        
        required_entries = [
            "*.db", "*.sqlite", "*.log", "*.pyc",
            "__pycache__/", ".env", ".venv", "venv/",
            "config/youtube/client_secrets.json",
            "data/*.db", "*.mp3", "*.mp4", "*.jpg"
        ]
        
        if not gitignore_path.exists():
            issues.append(".gitignore 文件不存在")
            return {"exists": False, "issues": issues}
        
        content = gitignore_path.read_text()
        missing = [entry for entry in required_entries if entry not in content]
        
        if missing:
            issues.append(f"缺少忽略规则: {', '.join(missing)}")
        
        return {
            "exists": True,
            "issues": issues,
            "missing_entries": missing,
            "passed": len(issues) == 0
        }
    
    def scan_sensitive_data(self):
        """扫描敏感信息泄露"""
        sensitive_files = []
        
        # 扫描配置文件
        for pattern_name, pattern in self.sensitive_patterns.items():
            # 扫描 .py 文件
            for py_file in self.workspace.rglob("*.py"):
                if "venv" in str(py_file) or "__pycache__" in str(py_file):
                    continue
                try:
                    content = py_file.read_text()
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        sensitive_files.append({
                            "file": str(py_file),
                            "pattern": pattern_name,
                            "matches": matches[:3]
                        })
                except:
                    pass
            
            # 扫描 .json 配置文件
            for json_file in self.workspace.rglob("*.json"):
                if "venv" in str(json_file):
                    continue
                try:
                    content = json_file.read_text()
                    if re.search(pattern, content, re.IGNORECASE):
                        sensitive_files.append({
                            "file": str(json_file),
                            "pattern": pattern_name,
                            "matches": ["发现敏感信息"]
                        })
                except:
                    pass
        
        # 检测硬编码密钥
        hardcoded = []
        for py_file in self.workspace.rglob("*.py"):
            if "venv" in str(py_file):
                continue
            try:
                content = py_file.read_text()
                if "UNSPLASH_KEY" in content and "ijXPXhcaX2k5neNoQAzN1cw8DJl3i9gx8FlRnzspqKs" in content:
                    hardcoded.append({"file": str(py_file), "type": "Unsplash Key"})
            except:
                pass
        
        return {
            "sensitive_found": len(sensitive_files),
            "sensitive_files": sensitive_files[:10],
            "hardcoded_keys": hardcoded,
            "risk_level": "high" if sensitive_files else "low"
        }
    
    def check_dependencies(self):
        """检查依赖安全（简单版本）"""
        requirements = self.workspace / "requirements.txt"
        if not requirements.exists():
            return {"exists": False, "issues": ["requirements.txt 不存在"]}
        
        content = requirements.read_text()
        packages = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
        
        # 检查已知危险包（示例）
        dangerous = ["requests<2.0", "flask<1.0"]
        found_dangerous = [p for p in packages if any(d in p for d in dangerous)]
        
        return {
            "total_packages": len(packages),
            "dangerous": found_dangerous,
            "passed": len(found_dangerous) == 0
        }
    
    def check_file_permissions(self):
        """检查敏感文件权限"""
        sensitive_paths = [
            "config/youtube/client_secrets.json",
            ".env",
            ".git/config"
        ]
        
        issues = []
        for sp in sensitive_paths:
            full_path = self.workspace / sp
            if full_path.exists():
                stat = full_path.stat()
                if stat.st_mode & 0o777 != 0o600:  # 不是只有所有者可读写
                    issues.append(f"{sp} 权限不安全: {oct(stat.st_mode)}")
        
        return {"issues": issues, "passed": len(issues) == 0}
    
    def full_audit(self):
        """完整安全审计"""
        self.log("开始安全审计...", "INFO")
        
        audit_result = {
            "timestamp": datetime.now().isoformat(),
            "gitignore": self.scan_gitignore(),
            "sensitive_data": self.scan_sensitive_data(),
            "dependencies": self.check_dependencies(),
            "permissions": self.check_file_permissions(),
            "overall_risk": "low",
            "recommendations": []
        }
        
        # 综合风险评估
        risk_score = 0
        if not audit_result["gitignore"]["passed"]:
            risk_score += 30
            audit_result["recommendations"].append("修复 .gitignore 配置")
        
        if audit_result["sensitive_data"]["sensitive_found"] > 0:
            risk_score += 50
            audit_result["recommendations"].append("移除硬编码的敏感信息")
        
        if not audit_result["permissions"]["passed"]:
            risk_score += 10
            audit_result["recommendations"].append("收紧敏感文件权限")
        
        if risk_score >= 50:
            audit_result["overall_risk"] = "high"
        elif risk_score >= 20:
            audit_result["overall_risk"] = "medium"
        
        # 保存报告
        with open(self.report_file, 'w') as f:
            json.dump(audit_result, f, ensure_ascii=False, indent=2)
        
        self.log(f"安全审计完成，风险等级: {audit_result['overall_risk']}", "INFO")
        
        return audit_result
    
    def show_report(self):
        """显示安全报告"""
        if not self.report_file.exists():
            self.full_audit()
        
        with open(self.report_file) as f:
            report = json.load(f)
        
        print("=" * 60)
        print("🛡️ 安全员报告")
        print("=" * 60)
        print(f"📅 审计时间: {report['timestamp']}")
        print(f"⚠️ 风险等级: {report['overall_risk'].upper()}")
        print(f"\n📋 .gitignore: {'✅ 正常' if report['gitignore']['passed'] else '❌ 有问题'}")
        print(f"🔑 敏感信息: {report['sensitive_data']['sensitive_found']} 处发现")
        print(f"📦 依赖检查: {'✅ 正常' if report['dependencies']['passed'] else '⚠️ 警告'}")
        print(f"🔒 文件权限: {'✅ 正常' if report['permissions']['passed'] else '❌ 有问题'}")
        
        if report["recommendations"]:
            print(f"\n💡 建议:\n   - " + "\n   - ".join(report["recommendations"]))
        
        print("=" * 60)

if __name__ == "__main__":
    security = SecurityAgent()
    
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "audit":
            result = security.full_audit()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif cmd == "report":
            security.show_report()
        elif cmd == "gitignore":
            result = security.scan_gitignore()
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif cmd == "sensitive":
            result = security.scan_sensitive_data()
            print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        security.show_report()
