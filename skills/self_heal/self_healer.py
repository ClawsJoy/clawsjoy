"""自愈 - 系统自己修复常见问题（知识库优先）"""
import os
import subprocess
import re
from lib.memory_simple import memory
from skills.error_knowledge_base import skill as knowledge_base

class SelfHealerSkill:
    name = "self_healer"
    description = "系统自愈（知识库优先）"
    version = "2.0.0"
    category = "debug"

    def _replace_placeholders(self, fix, error_msg):
        # 提取模块名
        module_match = re.search(r"named ['\"]?(\w+)", error_msg)
        if module_match and '<module>' in fix:
            fix = fix.replace('<module>', module_match.group(1))
        
        # 提取文件名
        file_match = re.search(r"['\"]([^'\"]+\.\w+)['\"]", error_msg)
        if file_match and '<file>' in fix:
            fix = fix.replace('<file>', file_match.group(1))
        
        # 提取路径
        path_match = re.search(r"['\"]([^'\"]+/\w+)['\"]", error_msg)
        if path_match and '<path>' in fix:
            fix = fix.replace('<path>', path_match.group(1))
        
        # 提取端口
        port_match = re.search(r'port (\d+)', error_msg.lower())
        if port_match and '<port>' in fix:
            fix = fix.replace('<port>', port_match.group(1))
        
        return fix

    def execute(self, params):
        error_msg = params.get("error", "")
        
        knowledge = knowledge_base.find_fix(error_msg)
        if knowledge and knowledge.get('fix'):
            fix = knowledge['fix']
            fix = self._replace_placeholders(fix, error_msg)
            print(f"📚 知识库匹配: {fix}")
            result = self._execute_fix(fix)
            if result.get('fixed'):
                return result
            else:
                return result
        
        if "ModuleNotFoundError" in error_msg or "No module named" in error_msg:
            return self._fix_module(error_msg)
        elif "FileNotFoundError" in error_msg or "No such file or directory" in error_msg:
            return self._fix_path(error_msg)
        elif "Connection refused" in error_msg and "11434" in error_msg:
            return self._fix_ollama()
        
        memory.remember(f"未知错误|{error_msg[:100]}", category="unknown_errors")
        return {"fixed": False, "message": "未知错误，已记录"}
    
    def _execute_fix(self, fix):
        try:
            if 'pip install' in fix:
                result = subprocess.run(fix, shell=True, capture_output=True)
                if result.returncode == 0:
                    return {"fixed": True, "action": fix}
                return {"fixed": False, "message": result.stderr.decode()[:100]}
            
            elif 'mkdir' in fix:
                os.makedirs(fix.replace('mkdir -p ', ''), exist_ok=True)
                return {"fixed": True, "action": fix}
            
            elif 'fuser -k' in fix:
                subprocess.run(fix, shell=True, capture_output=True)
                return {"fixed": True, "action": fix}
            
            elif 'ollama serve' in fix:
                subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return {"fixed": True, "action": fix}
            
            elif 'apt install' in fix:
                result = subprocess.run(fix, shell=True, capture_output=True)
                if result.returncode == 0:
                    return {"fixed": True, "action": fix}
                return {"fixed": False, "message": result.stderr.decode()[:100]}
            
            elif 'chmod' in fix:
                result = subprocess.run(fix, shell=True, capture_output=True)
                if result.returncode == 0:
                    return {"fixed": True, "action": fix}
                return {"fixed": False, "message": f"请手动执行: {fix}"}
            
            else:
                return {"fixed": False, "message": f"无法自动执行: {fix}"}
        except Exception as e:
            return {"fixed": False, "message": str(e)}
    
    def _fix_module(self, error_msg):
        match = re.search(r"named '?(\w+)'?", error_msg)
        if match:
            module = match.group(1)
            if module and module not in ['No', 'no']:
                result = subprocess.run(f"pip install {module}", shell=True, capture_output=True)
                if result.returncode == 0:
                    return {"fixed": True, "action": f"已安装模块: {module}"}
        return {"fixed": False, "message": "无法自动安装模块"}
    
    def _fix_path(self, error_msg):
        match = re.search(r"['\"]([^'\"]+\.(?:jpg|png|mp4|py|json))['\"]", error_msg)
        if match:
            path = match.group(1)
            dir_path = os.path.dirname(path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
                return {"fixed": True, "action": f"创建目录: {dir_path}"}
        return {"fixed": False, "message": "无法提取路径"}
    
    def _fix_ollama(self):
        subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return {"fixed": True, "action": "已启动 Ollama"}

skill = SelfHealerSkill()
