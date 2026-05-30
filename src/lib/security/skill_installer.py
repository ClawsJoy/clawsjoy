#!/usr/bin/env python3
"""Skill Installer - Skill Installer 模块

@version: 5.0.0
@author: ClawsJoy
@date: 2026-05-31
"""

from lib.smart_config import smart_config
"""技能安装安全检测器 - 自动检测并拒绝不安全技能"""
import re
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Tuple
from src.lib.security.skill_scanner import skill_scanner
from src.lib.security.community_validator import community_validator

class SkillInstaller:
    """技能安装器 - 带安全检测"""
    
    def __init__(self):
        self.install_log = Path("logs/skill_install.log")
        self.blocked_dir = Path("skills/blocked")
        self.blocked_dir.mkdir(parents=True, exist_ok=True)
    
    def install_from_file(self, file_path: str, source: str = "local") -> Dict:
        """从文件安装技能（带安全检测）"""
        path = Path(file_path)
        
        if not path.exists():
            return {"success": False, "error": "文件不存在"}
        
        # 1. 安全扫描
        print(f"🔍 安全扫描: {path.name}")
        scan_result = skill_scanner.scan_skill_file(str(path))
        
        if not scan_result.get("is_safe"):
            # 不安全：移动到隔离区
            dest = self.blocked_dir / path.name
            shutil.move(str(path), str(dest))
            self._log_install(path.name, "BLOCKED", scan_result)
            return {
                "success": False,
                "error": "技能被安全策略阻止",
                "reason": scan_result.get("issues", []),
                "risk_level": scan_result.get("risk_level"),
                "action": "moved_to_quarantine",
                "quarantine_path": str(dest)
            }
        
        # 2. 安全：移动到技能目录
        dest = Path("src/skills/atomic") / path.name
        shutil.copy(str(path), str(dest))
        self._log_install(path.name, "INSTALLED", scan_result)
        
        return {
            "success": True,
            "message": "技能安装成功",
            "destination": str(dest),
            "scan_result": scan_result
        }
    
    def install_from_url(self, url: str) -> Dict:
        """从 URL 下载并安装技能"""
        # 1. 验证 URL 来源
        url_result = community_validator.validate_url(url)
        
        if not url_result.get("is_trusted") and url_result.get("trust_level") != "high":
            return {
                "success": False,
                "error": "来源不可信",
                "warnings": url_result.get("warnings", []),
                "trust_level": url_result.get("trust_level")
            }
        
        # 2. 下载技能文件
        import requests
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code != 200:
                return {"success": False, "error": f"下载失败: HTTP {resp.status_code}"}
            
            skill_code = resp.text
        except Exception as e:
            return {"success": False, "error": f"下载异常: {e}"}
        
        # 3. 验证技能代码
        validate_result = community_validator.validate_skill(skill_code, url)
        
        if not validate_result.get("is_safe"):
            self._log_install(url.split('/')[-1], "BLOCKED", validate_result)
            return {
                "success": False,
                "error": "技能安全验证失败",
                "issues": validate_result.get("issues", []),
                "risk_level": validate_result.get("risk_level")
            }
        
        # 4. 保存到临时文件
        temp_file = Path("/tmp/community_skill.py")
        temp_file.write_text(skill_code, encoding='utf-8')
        
        # 5. 安装
        return self.install_from_file(str(temp_file), source=f"url:{url}")
    
    def install_from_community(self, skill_name: str, version: str = "latest") -> Dict:
        """从社区市场安装技能"""
        # 模拟社区市场下载
        # 实际应该从 OpenClaw 市场 API 获取
        community_url = f"https://raw.githubusercontent.com/ClawsJoy/community-skills/main/{skill_name}.py"
        return self.install_from_url(community_url)
    
    def _log_install(self, skill_name: str, status: str, details: Dict):
        """记录安装日志"""
        log_entry = f"{datetime.now().isoformat()} | {status} | {skill_name} | {details.get('risk_level', 'unknown')}\n"
        with open(self.install_log, 'a') as f:
            f.write(log_entry)
        
        # 同时记录到记忆系统
        try:
            from lib.memory_simple import memory
            memory.remember(
                f"skill_install|{skill_name}|{status}|{details.get('risk_level', 'unknown')}",
                category="skill_install_history"
            )
        except:
            pass

skill_installer = SkillInstaller()
