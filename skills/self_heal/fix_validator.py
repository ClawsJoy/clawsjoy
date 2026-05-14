"""修复验证器 - 验证修复是否成功"""
import subprocess
import re
import os
import time

class FixValidatorSkill:
    name = "fix_validator"
    description = "验证修复是否成功"
    version = "1.0.0"
    category = "debug"

    def execute(self, params):
        error_msg = params.get("error", "")
        fix = params.get("fix", "")
        
        if not fix:
            return {"valid": False, "reason": "无修复方案"}
        
        # Ollama 连接错误
        if "Connection refused" in error_msg and "11434" in error_msg:
            time.sleep(2)
            result = subprocess.run("curl -s http://127.0.0.1:11434/api/tags", 
                                   shell=True, capture_output=True)
            valid = result.returncode == 0
            return {"valid": valid, "message": "Ollama 服务已启动" if valid else "Ollama 未响应"}
        
        # 模块缺失
        if "ModuleNotFoundError" in error_msg or "No module named" in error_msg:
            module = re.search(r"named ['\"]?(\w+)", error_msg)
            if module:
                module_name = module.group(1)
                result = subprocess.run(f"python -c 'import {module_name}'", 
                                       shell=True, capture_output=True)
                valid = result.returncode == 0
                return {"valid": valid, "message": f"模块 {module_name} 已安装" if valid else "模块未安装"}
        
        # 文件/目录不存在
        if "FileNotFoundError" in error_msg or "No such file or directory" in error_msg:
            path_match = re.search(r"['\"]([^'\"]+)['\"]", error_msg)
            if path_match:
                path = path_match.group(1)
                valid = os.path.exists(path) or os.path.exists(os.path.dirname(path))
                return {"valid": valid, "message": "路径已存在" if valid else "路径仍不存在"}
        
        # 端口占用
        if "Address already in use" in error_msg:
            port_match = re.search(r'port (\d+)', error_msg)
            if port_match:
                port = port_match.group(1)
                result = subprocess.run(f"lsof -ti:{port}", shell=True, capture_output=True)
                valid = result.returncode != 0  # 端口空闲
                return {"valid": valid, "message": f"端口 {port} 已释放" if valid else f"端口 {port} 仍被占用"}
        
        return {"valid": None, "message": "无法自动验证"}

# 创建全局实例
skill = FixValidatorSkill()
