"""获取系统信息"""
import platform
import os
class GetSystemInfoSkill:
    def execute(self, params):
        return {
            "success": True,
            "os": platform.system(),
            "python": platform.python_version(),
            "hostname": platform.node(),
            "cwd": os.getcwd()
        }
skill = GetSystemInfoSkill()
