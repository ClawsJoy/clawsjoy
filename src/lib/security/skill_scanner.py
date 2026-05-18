from lib.smart_config import smart_config
"""技能安全扫描器 - 检测社区技能的合法性"""
import re
import ast
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

class SkillSecurityScanner:
    """技能安全扫描器"""
    
    # 危险模式检测
    DANGEROUS_PATTERNS = {
        # 文件系统危险操作
        'os.system': {'level': 'critical', 'msg': '执行系统命令'},
        'os.popen': {'level': 'critical', 'msg': '执行系统命令'},
        'subprocess.run': {'level': 'high', 'msg': '子进程调用'},
        'subprocess.Popen': {'level': 'high', 'msg': '子进程调用'},
        'eval': {'level': 'critical', 'msg': '动态代码执行'},
        'exec': {'level': 'critical', 'msg': '动态代码执行'},
        '__import__': {'level': 'high', 'msg': '动态导入'},
        'open(.*,.*w': {'level': 'medium', 'msg': '文件写入'},
        'open(.*,.*r': {'level': 'low', 'msg': '文件读取'},
        'requests.get': {'level': 'medium', 'msg': '网络请求'},
        'requests.post': {'level': 'medium', 'msg': '网络请求'},
        
        # 敏感信息泄露
        'os.environ': {'level': 'medium', 'msg': '读取环境变量'},
        'getpass': {'level': 'low', 'msg': '密码输入'},
        
        # 危险模块
        'pickle.load': {'level': 'high', 'msg': '反序列化'},
        'pickle.dump': {'level': 'medium', 'msg': '序列化'},
        'socket': {'level': 'medium', 'msg': '网络通信'},
    }
    
    # 允许的安全模块
    ALLOWED_MODULES = [
        'json', 'time', 'datetime', 're', 'math', 'random',
        'hashlib', 'base64', 'uuid', 'collections', 'itertools',
        'typing', 'dataclasses', 'pathlib'
    ]
    
    def __init__(self):
        self.scan_results = {}
        self.scan_history = []
    
    def scan_skill_file(self, file_path: str) -> Dict:
        """扫描单个技能文件"""
        path = Path(file_path)
        if not path.exists():
            return {"error": "文件不存在", "file": file_path}
        
        content = path.read_text(encoding='utf-8')
        
        result = {
            "file": str(path),
            "name": path.stem,
            "scan_time": datetime.now().isoformat(),
            "issues": [],
            "risk_level": "low",
            "is_safe": True
        }
        
        # 1. 检查危险模式
        for pattern, info in self.DANGEROUS_PATTERNS.items():
            if re.search(pattern, content, re.IGNORECASE):
                result["issues"].append({
                    "pattern": pattern,
                    "level": info['level'],
                    "message": info['msg']
                })
                if info['level'] in ['critical', 'high']:
                    result["is_safe"] = False
        
        # 2. 检查导入模块
        imports = self._extract_imports(content)
        for imp in imports:
            if imp not in self.ALLOWED_MODULES:
                # 检查是否是标准库
                if not self._is_stdlib(imp):
                    result["issues"].append({
                        "pattern": f"import {imp}",
                        "level": "medium",
                        "message": f"导入外部模块: {imp}"
                    })
        
        # 3. 计算风险等级
        risk_levels = [i['level'] for i in result['issues']]
        if 'critical' in risk_levels:
            result['risk_level'] = 'critical'
        elif 'high' in risk_levels:
            result['risk_level'] = 'high'
        elif 'medium' in risk_levels:
            result['risk_level'] = 'medium'
        elif risk_levels:
            result['risk_level'] = 'low'
        
        self.scan_results[path.stem] = result
        return result
    
    def _extract_imports(self, content: str) -> List[str]:
        """提取导入的模块"""
        imports = []
        patterns = [
            r'^import\s+(\w+)',
            r'^from\s+(\w+)\s+import',
        ]
        for line in content.split('\n'):
            for pattern in patterns:
                match = re.match(pattern, line.strip())
                if match:
                    imports.append(match.group(1))
        return imports
    
    def _is_stdlib(self, module_name: str) -> bool:
        """检查是否是 Python 标准库"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    def validate_manifest(self, manifest_path: str) -> Dict:
        """验证技能清单的合法性"""
        path = Path(manifest_path)
        if not path.exists():
            return {"error": "清单文件不存在"}
        
        import json
        with open(path, 'r') as f:
            manifest = json.load(f)
        
        result = {
            "file": str(path),
            "valid": True,
            "issues": []
        }
        
        # 检查必需字段
        required_fields = ['name', 'type', 'version', 'description', 'author']
        for field in required_fields:
            if field not in manifest:
                result["issues"].append(f"缺少必需字段: {field}")
                result["valid"] = False
        
        # 检查版本格式
        if 'version' in manifest:
            if not re.match(r'^\d+\.\d+\.\d+$', manifest['version']):
                result["issues"].append(f"版本格式不正确: {manifest['version']}")
        
        return result
    
    def generate_report(self) -> Dict:
        """生成安全报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_scanned": len(self.scan_results),
            "safe_count": sum(1 for r in self.scan_results.values() if r.get('is_safe')),
            "unsafe_count": sum(1 for r in self.scan_results.values() if not r.get('is_safe')),
            "risk_breakdown": {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0
            },
            "results": self.scan_results
        }
        
        for r in self.scan_results.values():
            level = r.get('risk_level', 'low')
            if level in report["risk_breakdown"]:
                report["risk_breakdown"][level] += 1
        
        return report

skill_scanner = SkillSecurityScanner()
