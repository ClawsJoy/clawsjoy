from lib.smart_config import smart_config
"""社区技能验证器"""
import requests
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

class CommunitySkillValidator:
    """社区技能验证器"""
    
    # 可信源列表
    TRUSTED_SOURCES = {
        'github.com/ClawsJoy': 'high',
        'github.com/openclaw': 'high',
        'raw.githubusercontent.com': 'medium',
    }
    
    def __init__(self):
        self.download_history = []
        self.blocked_hashes = self._load_blocked()
    
    def _load_blocked(self) -> set:
        """加载黑名单哈希"""
        blocked_file = Path("data/blocked_skill_hashes.json")
        if blocked_file.exists():
            with open(blocked_file, 'r') as f:
                return set(json.load(f))
        return set()
    
    def validate_url(self, url: str) -> Dict:
        """验证下载源 URL"""
        result = {
            "url": url,
            "is_trusted": False,
            "trust_level": "unknown",
            "warnings": []
        }
        
        for trusted_source, level in self.TRUSTED_SOURCES.items():
            if trusted_source in url:
                result["is_trusted"] = True
                result["trust_level"] = level
                break
        
        if not result["is_trusted"]:
            result["warnings"].append("来源不在可信列表中")
        
        return result
    
    def validate_skill(self, skill_code: str, source_url: str = None) -> Dict:
        """验证下载的技能代码"""
        # 计算哈希
        skill_hash = hashlib.sha256(skill_code.encode()).hexdigest()
        
        # 检查黑名单
        if skill_hash in self.blocked_hashes:
            return {
                "is_safe": False,
                "error": "该技能已被标记为不安全",
                "hash": skill_hash
            }
        
        # 保存到临时文件进行扫描
        temp_file = Path("/tmp/community_skill_temp.py")
        temp_file.write_text(skill_code, encoding='utf-8')
        
        # 使用扫描器扫描
        from src.lib.security.skill_scanner import skill_scanner
        scan_result = skill_scanner.scan_skill_file(str(temp_file))
        
        # 清理临时文件
        temp_file.unlink()
        
        return {
            "is_safe": scan_result.get('is_safe', False),
            "risk_level": scan_result.get('risk_level', 'unknown'),
            "issues": scan_result.get('issues', []),
            "hash": skill_hash
        }
    
    def report_unsafe(self, skill_hash: str, reason: str):
        """报告不安全的技能"""
        self.blocked_hashes.add(skill_hash)
        blocked_file = Path("data/blocked_skill_hashes.json")
        with open(blocked_file, 'w') as f:
            json.dump(list(self.blocked_hashes), f, indent=2)
        print(f"⚠️ 已标记不安全技能: {skill_hash} - {reason}")

community_validator = CommunitySkillValidator()
